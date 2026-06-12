const SparkleIcon = ({ className, size = "lg" }) => {
    const sizeClasses = size === "sm"
        ? "w-8 h-8"
        : "w-16 h-16";
    const iconSizeClasses = size === "sm"
        ? "w-4 h-4"
        : "w-9 h-9";
    // For small size, return just the icon without the container
    if (size === "sm") {
        return (<svg viewBox="0 0 24 24" fill="none" className={`${iconSizeClasses} text-white ${className || ""}`} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4.5 12.5a4 4 0 0 0 4 4h1a1 1 0 0 0 1-1v-3"/>
        <path d="M19.5 12.5a4 4 0 0 1-4 4h-1a1 1 0 0 1-1-1v-3"/>
        <path d="M4.5 12.5V6a1 1 0 0 1 1-1h1"/>
        <path d="M19.5 12.5V6a1 1 0 0 0-1-1h-1"/>
        <circle cx="6.5" cy="4" r="1" fill="currentColor"/>
        <circle cx="17.5" cy="4" r="1" fill="currentColor"/>
        <circle cx="12" cy="19" r="2" fill="currentColor"/>
      </svg>);
    }
    return (<div className={`${sizeClasses} rounded-xl bg-primary flex items-center justify-center relative ${className || ""}`}>
      {/* Stethoscope */}
      <svg viewBox="0 0 24 24" fill="none" className="w-9 h-9 text-white" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        {/* Stethoscope tubing */}
        <path d="M4.5 12.5a4 4 0 0 0 4 4h1a1 1 0 0 0 1-1v-3"/>
        <path d="M19.5 12.5a4 4 0 0 1-4 4h-1a1 1 0 0 1-1-1v-3"/>
        {/* Ear pieces */}
        <path d="M4.5 12.5V6a1 1 0 0 1 1-1h1"/>
        <path d="M19.5 12.5V6a1 1 0 0 0-1-1h-1"/>
        {/* Ear tips */}
        <circle cx="6.5" cy="4" r="1" fill="currentColor"/>
        <circle cx="17.5" cy="4" r="1" fill="currentColor"/>
        {/* Chest piece */}
        <circle cx="12" cy="19" r="2" fill="currentColor"/>
      </svg>
      {/* Small clipboard accent */}
      <div className="absolute -bottom-1 -right-1 w-5 h-6 bg-white rounded-sm flex items-center justify-center">
        <svg viewBox="0 0 12 14" className="w-3 h-3.5 text-primary">
          <rect x="1" y="2" width="10" height="11" rx="1" fill="none" stroke="currentColor" strokeWidth="1.2"/>
          <rect x="3" y="0" width="6" height="3" rx="0.5" fill="currentColor"/>
          <line x1="3.5" y1="6" x2="8.5" y2="6" stroke="currentColor" strokeWidth="0.8"/>
          <line x1="3.5" y1="8" x2="8.5" y2="8" stroke="currentColor" strokeWidth="0.8"/>
          <line x1="3.5" y1="10" x2="6.5" y2="10" stroke="currentColor" strokeWidth="0.8"/>
        </svg>
      </div>
    </div>);
};
export default SparkleIcon;
