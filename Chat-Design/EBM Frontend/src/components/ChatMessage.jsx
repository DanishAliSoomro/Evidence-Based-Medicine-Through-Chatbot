import { User, Copy, Bookmark, Check } from "lucide-react";
import { useState } from "react";
import SparkleIcon from "./SparkleIcon";
import { toast } from "@/hooks/use-toast";
const ChatMessage = ({ message, onBookmark }) => {
    const isUser = message.role === "user";
    const [copied, setCopied] = useState(false);
    const handleCopy = async () => {
        await navigator.clipboard.writeText(message.content);
        setCopied(true);
        toast({ title: "Copied to clipboard" });
        setTimeout(() => setCopied(false), 2000);
    };
    const handleBookmark = () => {
        onBookmark?.(message.id);
        toast({
            title: message.bookmarked ? "Removed from bookmarks" : "Added to bookmarks"
        });
    };
    return (<div className="flex gap-4 py-4 px-6">
      {/* Avatar */}
      <div className="flex-shrink-0">
        {isUser ? (<div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center">
            <User className="w-4 h-4 text-white"/>
          </div>) : (<div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
            <SparkleIcon size="sm"/>
          </div>)}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        <p className="text-foreground leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
        
        {/* Action buttons for assistant messages */}
        {!isUser && (<div className="flex items-center gap-2 mt-3">
            <button onClick={handleCopy} className="p-1.5 rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground" title="Copy">
              {copied ? (<Check className="w-4 h-4"/>) : (<Copy className="w-4 h-4"/>)}
            </button>
            <button onClick={handleBookmark} className="p-1.5 rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground" title="Bookmark">
              <Bookmark className={`w-4 h-4 ${message.bookmarked ? 'fill-current' : ''}`}/>
            </button>
          </div>)}
      </div>
    </div>);
};
export default ChatMessage;
