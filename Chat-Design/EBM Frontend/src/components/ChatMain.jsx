import { useRef, useEffect } from "react";
import { useLanguage } from "@/hooks/use-language";
import SparkleIcon from "./SparkleIcon";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
const s = (lang, en, ur) => (lang === "ur" ? ur : en);

const ChatMain = ({ messages, onSendMessage, onBookmark, isLoading, sidebarOpen, onToggleSidebar }) => {
    const messagesEndRef = useRef(null);
    const [lang] = useLanguage();
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);
    const hasMessages = messages.length > 0;
    return (<main className="flex-1 h-screen flex flex-col bg-background">
      {/* Messages Area or Welcome Screen */}
      <div className="flex-1 overflow-y-auto">
        {hasMessages ? (<div className="max-w-4xl mx-auto">
            {messages.map((message) => (<ChatMessage key={message.id} message={message} onBookmark={onBookmark}/>))}
            {isLoading && (<div className="flex gap-4 py-4 px-6">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                  <SparkleIcon size="sm"/>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "0ms" }}/>
                  <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "150ms" }}/>
                  <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "300ms" }}/>
                </div>
              </div>)}
            <div ref={messagesEndRef}/>
          </div>) : (<div className="h-full flex flex-col items-center justify-center px-6">
            <SparkleIcon />
            
            <h1 className="mt-6 text-2xl font-semibold text-foreground text-center">
              Evidence Based Medicine Chatbot
            </h1>
            
            <p className="mt-3 text-muted-foreground text-center max-w-xl">
              {s(lang, "Ask me anything about medical research, clinical guidelines, or evidence-based practices", "طبی تحقیق، طبی رہنما اصولوں، یا شواہد پر مبنی طریقوں کے بارے میں کچھ بھی پوچھیں")}
            </p>
          </div>)}
      </div>

      {/* Input Area */}
      <div className="px-6 pb-6">
        <ChatInput onSend={onSendMessage} disabled={isLoading}/>
        
        <p className="mt-4 text-sm text-muted-foreground text-center">
          {s(lang, "This chatbot provides information for educational purposes. Always consult healthcare professionals for medical decisions.", "یہ چیٹ بوٹ صرف تعلیمی مقاصد کے لیے معلومات فراہم کرتا ہے۔ طبی فیصلوں کے لیے ہمیشہ صحت کے ماہرین سے مشورہ کریں۔")}
        </p>
      </div>
    </main>);
};
export default ChatMain;
