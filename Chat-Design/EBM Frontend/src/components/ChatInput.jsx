import { Send, Paperclip, Image, FileText, X } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useLanguage } from "@/hooks/use-language";

const ChatInput = ({ onSend, disabled }) => {
    const [message, setMessage]         = useState("");
    const [showAttachMenu, setShowAttachMenu] = useState(false);
    const [attachment, setAttachment]   = useState(null); // { name, type, dataUrl, isImage }
    const fileInputRef  = useRef(null);
    const textareaRef   = useRef(null);
    const [lang]        = useLanguage();

    // Auto-resize textarea height as user types
    useEffect(() => {
        const ta = textareaRef.current;
        if (!ta) return;
        ta.style.height = "auto";
        ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`;
    }, [message]);

    const readFile = (file) => {
        if (!file) return;
        const isImage = file.type.startsWith("image/");
        const isPdf   = file.type === "application/pdf";
        if (!isImage && !isPdf) return;
        const reader = new FileReader();
        reader.onload = (e) =>
            setAttachment({ name: file.name, type: file.type, dataUrl: e.target.result, isImage });
        reader.readAsDataURL(file);
    };

    const handleFileChange = (e) => {
        readFile(e.target.files?.[0]);
        e.target.value = "";
        setShowAttachMenu(false);
    };

    const handleAttachClick = (type) => {
        if (fileInputRef.current) {
            fileInputRef.current.accept = type === "image" ? "image/*" : "application/pdf";
            fileInputRef.current.click();
        }
        setShowAttachMenu(false);
    };

    const handlePaste = (e) => {
        const items = Array.from(e.clipboardData?.items || []);
        const imageItem = items.find((item) => item.type.startsWith("image/"));
        if (imageItem) {
            e.preventDefault();
            readFile(imageItem.getAsFile());
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
        }
    };

    const submit = () => {
        if (!message.trim() || disabled) return;
        onSend({ content: message.trim(), attachment });
        setMessage("");
        setAttachment(null);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        submit();
    };

    return (
        <form onSubmit={handleSubmit} className="relative w-full max-w-3xl mx-auto">
            <div className="flex flex-col rounded-2xl border border-border bg-card shadow-sm focus-within:ring-2 focus-within:ring-primary/20 transition-shadow">

                {/* Attachment chip — shown inside the box when a file is attached */}
                {attachment && (
                    <div className="px-4 pt-3">
                        {attachment.isImage ? (
                            <div className="relative group inline-block">
                                <img
                                    src={attachment.dataUrl}
                                    alt={attachment.name}
                                    className="h-16 w-16 rounded-xl object-cover border border-border"
                                />
                                <button
                                    type="button"
                                    onClick={() => setAttachment(null)}
                                    className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-foreground text-background rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <X className="w-3 h-3" />
                                </button>
                            </div>
                        ) : (
                            <div className="relative group inline-flex items-center gap-2 pl-2 pr-8 py-2 bg-muted rounded-xl border border-border max-w-[220px]">
                                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                                    <FileText className="w-4 h-4 text-primary" />
                                </div>
                                <div className="min-w-0">
                                    <p className="text-xs font-medium text-foreground truncate max-w-[130px]">{attachment.name}</p>
                                    <p className="text-xs text-muted-foreground">PDF</p>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => setAttachment(null)}
                                    className="absolute top-1 right-1 w-5 h-5 bg-foreground text-background rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <X className="w-3 h-3" />
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Textarea */}
                <textarea
                    ref={textareaRef}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onPaste={handlePaste}
                    placeholder={
                        lang === "ur"
                            ? "طبی شواہد، تحقیق، یا طبی رہنما اصولوں کے بارے میں پوچھیں..."
                            : "Ask about medical evidence, research, or clinical guidelines..."
                    }
                    rows={1}
                    disabled={disabled}
                    className="w-full bg-transparent px-4 pt-3 pb-2 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none min-h-[44px] max-h-[200px] overflow-y-auto leading-relaxed"
                />

                {/* Bottom bar */}
                <div className="flex items-center justify-between px-3 pb-3 pt-1">
                    {/* Attach button */}
                    <div className="relative">
                        <button
                            type="button"
                            onClick={() => setShowAttachMenu((p) => !p)}
                            className="w-9 h-9 rounded-full flex items-center justify-center text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                            title="Attach file"
                        >
                            <Paperclip className="w-5 h-5" />
                        </button>

                        {showAttachMenu && (
                            <div className="absolute left-0 bottom-full mb-2 bg-popover border border-border rounded-xl shadow-lg p-1.5 z-20 min-w-[140px]">
                                <button
                                    type="button"
                                    onClick={() => handleAttachClick("image")}
                                    className="flex items-center gap-3 w-full px-3 py-2 text-sm text-foreground hover:bg-muted rounded-lg transition-colors"
                                >
                                    <Image className="w-4 h-4" />
                                    <span>Image</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => handleAttachClick("pdf")}
                                    className="flex items-center gap-3 w-full px-3 py-2 text-sm text-foreground hover:bg-muted rounded-lg transition-colors"
                                >
                                    <FileText className="w-4 h-4" />
                                    <span>PDF</span>
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Send button */}
                    <button
                        type="submit"
                        disabled={!message.trim() || disabled}
                        className="w-9 h-9 rounded-full bg-foreground flex items-center justify-center text-background disabled:opacity-30 hover:opacity-80 transition-opacity"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </div>

            <input ref={fileInputRef} type="file" onChange={handleFileChange} className="hidden" />
        </form>
    );
};

export default ChatInput;
