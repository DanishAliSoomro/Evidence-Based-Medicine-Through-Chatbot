import { Send, Paperclip, Image, FileText, X } from "lucide-react";
import { useState, useRef } from "react";
import { useLanguage } from "@/hooks/use-language";
const ChatInput = ({ onSend, disabled }) => {
    const [message, setMessage] = useState("");
    const [showAttachMenu, setShowAttachMenu] = useState(false);
    const fileInputRef = useRef(null);
    const [attachmentType, setAttachmentType] = useState(null);
    const [lang] = useLanguage();
    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() && !disabled) {
            onSend(message.trim());
            setMessage("");
        }
    };
    const handleAttachClick = (type) => {
        setAttachmentType(type);
        if (fileInputRef.current) {
            fileInputRef.current.accept = type === "image" ? "image/*" : "application/pdf";
            fileInputRef.current.click();
        }
        setShowAttachMenu(false);
    };
    const handleFileChange = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            console.log(`${attachmentType} attached:`, file.name);
            // File handling logic would go here
        }
    };
    return (<form onSubmit={handleSubmit} className="relative w-full max-w-3xl mx-auto">
      <div className="relative flex items-center">
        {/* Attachment Button */}
        <div className="relative">
          <button type="button" onClick={() => setShowAttachMenu(!showAttachMenu)} className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-muted flex items-center justify-center text-muted-foreground hover:bg-primary hover:text-primary-foreground transition-colors z-10">
            {showAttachMenu ? <X className="w-5 h-5"/> : <Paperclip className="w-5 h-5"/>}
          </button>

          {/* Attachment Menu */}
          {showAttachMenu && (<div className="absolute left-0 bottom-full mb-2 bg-card border border-border rounded-lg shadow-lg p-2 z-20 min-w-[140px]">
              <button type="button" onClick={() => handleAttachClick("image")} className="flex items-center gap-3 w-full px-3 py-2 text-sm text-foreground hover:bg-muted rounded-md transition-colors">
                <Image className="w-4 h-4"/>
                <span>Image</span>
              </button>
              <button type="button" onClick={() => handleAttachClick("pdf")} className="flex items-center gap-3 w-full px-3 py-2 text-sm text-foreground hover:bg-muted rounded-md transition-colors">
                <FileText className="w-4 h-4"/>
                <span>PDF</span>
              </button>
            </div>)}
        </div>

        <input type="text" value={message} onChange={(e) => setMessage(e.target.value)} placeholder={lang === "ur" ? "طبی شواہد، تحقیق، یا طبی رہنما اصولوں کے بارے میں پوچھیں..." : "Ask about medical evidence, research, or clinical guidelines..."} className="chat-input pl-16" disabled={disabled}/>
        <button type="submit" disabled={!message.trim() || disabled} className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-muted flex items-center justify-center text-muted-foreground hover:bg-primary hover:text-primary-foreground disabled:opacity-50 disabled:hover:bg-muted disabled:hover:text-muted-foreground transition-colors">
          <Send className="w-5 h-5"/>
        </button>
      </div>

      {/* Hidden file input */}
      <input ref={fileInputRef} type="file" onChange={handleFileChange} className="hidden"/>
    </form>);
};
export default ChatInput;
