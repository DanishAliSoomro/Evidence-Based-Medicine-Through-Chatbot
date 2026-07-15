import { User, Copy, Bookmark, Check, FileText, X, ZoomIn } from "lucide-react";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SparkleIcon from "./SparkleIcon";
import { toast } from "@/hooks/use-toast";

const ImageLightbox = ({ src, alt, onClose }) => {
    useEffect(() => {
        const handleKey = (e) => { if (e.key === "Escape") onClose(); };
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [onClose]);

    return (
        <div
            className="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-4"
            onClick={onClose}
        >
            <button
                onClick={onClose}
                className="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
            >
                <X className="w-5 h-5" />
            </button>
            <img
                src={src}
                alt={alt}
                className="max-h-[90vh] max-w-[90vw] rounded-xl object-contain shadow-2xl"
                onClick={(e) => e.stopPropagation()}
            />
        </div>
    );
};

const ChatMessage = ({ message, onBookmark }) => {
    const isUser = message.role === "user";
    const [copied, setCopied]   = useState(false);
    const [lightbox, setLightbox] = useState(false);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(message.content);
        setCopied(true);
        toast({ title: "Copied to clipboard" });
        setTimeout(() => setCopied(false), 2000);
    };

    const handleBookmark = () => {
        onBookmark?.(message.id);
        toast({ title: message.bookmarked ? "Removed from bookmarks" : "Added to bookmarks" });
    };

    return (
        <>
            <div className="flex gap-4 py-4 px-6">
                {/* Avatar */}
                <div className="flex-shrink-0">
                    {isUser ? (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center">
                            <User className="w-4 h-4 text-white" />
                        </div>
                    ) : (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                            <SparkleIcon size="sm" />
                        </div>
                    )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    {/* Attachment */}
                    {message.attachment && (
                        <div className="mb-3">
                            {message.attachment.isImage ? (
                                <div
                                    className="relative group inline-block cursor-zoom-in"
                                    onClick={() => setLightbox(true)}
                                >
                                    <img
                                        src={message.attachment.dataUrl}
                                        alt={message.attachment.name}
                                        className="max-h-56 max-w-xs rounded-xl object-cover border border-border group-hover:brightness-90 transition-all"
                                    />
                                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                        <div className="bg-black/40 rounded-full p-2">
                                            <ZoomIn className="w-5 h-5 text-white" />
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="inline-flex items-center gap-2 px-3 py-2 bg-muted border border-border rounded-xl">
                                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                                        <FileText className="w-4 h-4 text-primary" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-foreground">{message.attachment.name}</p>
                                        <p className="text-xs text-muted-foreground">PDF</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Text */}
                    {message.content && (
                        isUser ? (
                            <p className="text-foreground leading-relaxed whitespace-pre-wrap">
                                {message.content}
                            </p>
                        ) : (
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                    p:      ({ children }) => <p className="text-foreground leading-relaxed mb-2 last:mb-0">{children}</p>,
                                    strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
                                    em:     ({ children }) => <em className="italic text-foreground">{children}</em>,
                                    h1:     ({ children }) => <h1 className="text-xl font-bold text-foreground mt-3 mb-1">{children}</h1>,
                                    h2:     ({ children }) => <h2 className="text-lg font-semibold text-foreground mt-3 mb-1">{children}</h2>,
                                    h3:     ({ children }) => <h3 className="text-base font-semibold text-foreground mt-2 mb-1">{children}</h3>,
                                    ul:     ({ children }) => <ul className="list-disc pl-5 space-y-0.5 mb-2 text-foreground">{children}</ul>,
                                    ol:     ({ children }) => <ol className="list-decimal pl-5 space-y-0.5 mb-2 text-foreground">{children}</ol>,
                                    li:     ({ children }) => <li className="text-foreground leading-relaxed [&>p]:inline [&>p]:mb-0">{children}</li>,
                                    code:   ({ inline, children }) => inline
                                        ? <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono text-foreground">{children}</code>
                                        : <pre className="bg-muted p-3 rounded-lg text-sm font-mono overflow-x-auto mb-2"><code>{children}</code></pre>,
                                    blockquote: ({ children }) => <blockquote className="border-l-4 border-primary/40 pl-3 italic text-muted-foreground mb-2">{children}</blockquote>,
                                    hr:     () => <hr className="border-border my-3" />,
                                }}
                            >
                                {message.content}
                            </ReactMarkdown>
                        )
                    )}

                    {/* Action buttons — assistant only */}
                    {!isUser && (
                        <div className="flex items-center gap-2 mt-3">
                            <button
                                onClick={handleCopy}
                                className="p-1.5 rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                                title="Copy"
                            >
                                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                            </button>
                            <button
                                onClick={handleBookmark}
                                className="p-1.5 rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                                title="Bookmark"
                            >
                                <Bookmark className={`w-4 h-4 ${message.bookmarked ? "fill-current" : ""}`} />
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Lightbox */}
            {lightbox && message.attachment?.isImage && (
                <ImageLightbox
                    src={message.attachment.dataUrl}
                    alt={message.attachment.name}
                    onClose={() => setLightbox(false)}
                />
            )}
        </>
    );
};

export default ChatMessage;
