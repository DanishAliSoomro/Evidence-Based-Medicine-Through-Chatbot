import * as React from "react";
import { useState, useMemo } from "react";
import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu";
import { MessageSquare, MoreHorizontal, Trash2, Search, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

/* ---------- DropdownMenu ---------- */
const DropdownMenu        = DropdownMenuPrimitive.Root;
const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger;
const DropdownMenuContent = React.forwardRef(({ className, sideOffset = 4, ...props }, ref) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        "z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
        className,
      )}
      {...props}
    />
  </DropdownMenuPrimitive.Portal>
));
const DropdownMenuItem = React.forwardRef(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={cn(
      "relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className,
    )}
    {...props}
  />
));

/* ====================================================================
   ConversationList
   Props:
     conversations  — array of { id, numId, title, preview, timestamp }
     activeChat     — id of currently open conversation (string)
     onSelectChat   — (id) => void
     onDeleteChat   — (id) => void
   ==================================================================== */
const ConversationList = ({ conversations, activeChat, onSelectChat, onDeleteChat }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  const filtered = useMemo(() => {
    if (!searchQuery.trim()) return conversations;
    const q = searchQuery.toLowerCase();
    return conversations.filter(
      (c) => c.title.toLowerCase().includes(q) || c.preview.toLowerCase().includes(q),
    );
  }, [conversations, searchQuery]);

  const handleDelete = (id, title) => {
    onDeleteChat(id);
    toast({ title: "Chat deleted", description: `"${title}" was removed.` });
  };

  const toggleSearch = () => {
    setIsSearching((prev) => !prev);
    setSearchQuery("");
  };

  return (
    <>
      {/* ── Search bar ── */}
      <div className="px-3 pb-2 space-y-2">
        <button onClick={toggleSearch} className="sidebar-item w-full">
          <Search className="w-5 h-5" />
          <span>Search chats</span>
        </button>

        {isSearching && (
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="w-full px-3 py-2 pr-8 bg-sidebar-accent text-sidebar-foreground placeholder:text-sidebar-foreground/50 rounded-lg text-sm border border-sidebar-border focus:outline-none focus:ring-1 focus:ring-primary"
              autoFocus
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-sidebar-foreground/50 hover:text-sidebar-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* ── Conversation rows ── */}
      <div className="flex-1 px-3 overflow-y-auto space-y-1">
        {filtered.length > 0 ? (
          filtered.map((conv) => (
            <div
              key={conv.id}
              className={`group relative flex items-center rounded-lg ${
                activeChat === conv.id ? "bg-sidebar-accent" : "hover:bg-sidebar-accent/60"
              }`}
            >
              <button
                onClick={() => onSelectChat(conv.id)}
                className="flex items-center gap-2 flex-1 min-w-0 px-3 py-2 text-left text-sidebar-foreground"
              >
                <MessageSquare className="w-5 h-5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="truncate text-sm">{conv.title}</p>
                  <p className="truncate text-xs text-sidebar-foreground/60">{conv.preview}</p>
                </div>
              </button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    onClick={(e) => e.stopPropagation()}
                    className="opacity-0 group-hover:opacity-100 data-[state=open]:opacity-100 p-1.5 mr-1 rounded-md hover:bg-sidebar-accent text-sidebar-foreground/70 hover:text-sidebar-foreground transition-opacity"
                    title="Chat options"
                  >
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-40 bg-popover border border-border">
                  <DropdownMenuItem
                    onClick={() => handleDelete(conv.id, conv.title)}
                    className="flex items-center gap-2 cursor-pointer text-destructive focus:text-destructive"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Delete</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ))
        ) : searchQuery ? (
          <p className="text-sm text-sidebar-foreground/50 text-center py-4">No chats found</p>
        ) : (
          <p className="text-sm text-sidebar-foreground/50 text-center py-4">No conversations yet</p>
        )}
      </div>
    </>
  );
};

export default ConversationList;
