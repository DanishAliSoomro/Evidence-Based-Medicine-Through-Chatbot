import { AlertTriangle, ChevronDown } from "lucide-react";

const buttonBase =
  "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";
const buttonVariants = {
  default: "bg-primary text-primary-foreground hover:bg-primary/90",
  outline: "border border-input bg-background text-foreground hover:bg-accent hover:text-accent-foreground",
  destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
};
const buttonSizes = { default: "h-10 px-4 py-2", sm: "h-9 px-3", lg: "h-11 px-6", icon: "h-10 w-10" };

export const Button = ({ variant = "default", size = "default", className = "", ...props }) => (
  <button
    className={`${buttonBase} ${buttonVariants[variant] ?? buttonVariants.default} ${buttonSizes[size] ?? buttonSizes.default} ${className}`}
    {...props}
  />
);

export const Input = ({ className = "", ...props }) => (
  <input
    className={`flex w-full rounded-md border border-input px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    {...props}
  />
);

export const Switch = ({ checked, onCheckedChange }) => (
  <button
    role="switch"
    aria-checked={checked}
    onClick={() => onCheckedChange(!checked)}
    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${checked ? "bg-primary" : "bg-muted"}`}
  >
    <span
      className={`inline-block h-4 w-4 rounded-full bg-white shadow transition-transform ${checked ? "translate-x-6" : "translate-x-1"}`}
    />
  </button>
);

export const SelectBox = ({ value, onChange, options }) => (
  <div className="relative w-36">
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="h-10 w-full appearance-none rounded-md border border-input bg-background px-3 pr-9 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
    <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
  </div>
);

export const Section = ({ title, desc, children }) => (
  <div>
    <div className="mb-8">
      <h2 className="text-2xl font-bold text-foreground mb-2">{title}</h2>
      <p className="text-muted-foreground">{desc}</p>
    </div>
    <div className="space-y-5">{children}</div>
  </div>
);

export const Row = ({ icon: Icon, title, desc, children }) => (
  <div className="flex items-center justify-between gap-4 p-4 rounded-xl bg-card border border-border">
    <div className="flex items-start gap-3 min-w-0">
      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-primary" />
      </div>
      <div className="min-w-0">
        <p className="font-medium text-foreground">{title}</p>
        <p className="text-sm text-muted-foreground">{desc}</p>
      </div>
    </div>
    <div className="flex-shrink-0">{children}</div>
  </div>
);

export const DeleteDialog = ({ onConfirm, onCancel, isUrdu }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
    <div
      className="relative w-full max-w-sm mx-4 rounded-2xl border border-border bg-card p-6 shadow-2xl"
      dir={isUrdu ? "rtl" : "ltr"}
    >
      <div className="flex flex-col items-center text-center gap-4">
        <div className="w-14 h-14 rounded-full bg-destructive/10 flex items-center justify-center">
          <AlertTriangle className="w-7 h-7 text-destructive" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-foreground mb-1">
            {isUrdu ? "اکاؤنٹ حذف کریں؟" : "Delete account?"}
          </h3>
          <p className="text-sm text-muted-foreground">
            {isUrdu
              ? "یہ عمل مستقل ہے اور واپس نہیں ہو سکتا۔ آپ کی تمام گفتگوئیں، تاریخ اور ترجیحات مٹ جائیں گی۔"
              : "This action is permanent and cannot be undone. All your chats, history and preferences will be erased."}
          </p>
        </div>
        <div className="flex gap-3 w-full mt-2">
          <Button variant="outline" className="flex-1" onClick={onCancel}>
            {isUrdu ? "رد کریں" : "Cancel"}
          </Button>
          <Button variant="destructive" className="flex-1" onClick={onConfirm}>
            {isUrdu ? "ہاں، حذف کریں" : "Yes, delete"}
          </Button>
        </div>
      </div>
    </div>
  </div>
);
