import * as React from "react";
import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Mail, Lock, Eye, EyeOff, ArrowRight, UserCircle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import SparkleIcon from "@/components/SparkleIcon";
import { registerUser } from "@/api/chatApi";

const Input = React.forwardRef(({ className, type, ...props }, ref) => (
  <input
    type={type}
    ref={ref}
    className={cn(
      "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
      className,
    )}
    {...props}
  />
));

const Signup = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/";


  const [username, setUsername]   = useState("");
  const [email, setEmail]         = useState("");
  const [password, setPassword]   = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [showPw, setShowPw]       = useState(false);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPw) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    if (!email.trim()) {
      setError("Email is required.");
      return;
    }

    setLoading(true);
    try {
      await registerUser(username.trim(), email.trim(), password);
      navigate("/login?registered=1", { replace: true });
    } catch (err) {
      let msg = err.message || "Sign up failed.";
      try { msg = JSON.parse(msg).detail || msg; } catch {}
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Brand panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[hsl(217,50%,15%)] via-[hsl(217,45%,20%)] to-[hsl(217,40%,12%)] relative overflow-hidden">
        <div className="absolute top-1/4 -left-20 w-80 h-80 bg-emerald-500/30 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-10 w-60 h-60 bg-emerald-500/20 rounded-full blur-3xl" />
        <div className="relative z-10 flex flex-col justify-center items-center px-16 w-full gap-6">
          <div className="flex items-center gap-3">
            <div className="w-14 h-14 rounded-xl bg-emerald-500 flex items-center justify-center">
              <SparkleIcon className="w-8 h-8 text-white" />
            </div>
            <span className="text-3xl font-bold text-white">EBM AI</span>
          </div>
          <h1 className="text-4xl font-bold text-white leading-tight text-center">
            Join EBM AI<br />
            <span className="text-emerald-400">Evidence-Based Medicine</span>
          </h1>
          <p className="text-white/70 text-lg max-w-md text-center">
            Create your account to start querying clinical evidence, save your conversations, and share findings with colleagues.
          </p>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex-1 flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-3 mb-10 justify-center">
            <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center">
              <SparkleIcon className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-foreground">EBM AI</span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-foreground mb-1">Sign up</h2>
            <p className="text-muted-foreground text-sm">All fields marked * are required.</p>
          </div>

          {error && (
            <div className="mb-5 flex items-center gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Username *</label>
              <div className="relative">
                <UserCircle className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="dr_smith"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="pl-12 h-12 bg-card"
                  required
                />
              </div>
              <p className="text-xs text-muted-foreground"></p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Email *</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type="email"
                  placeholder="dr@hospital.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-12 h-12 bg-card"
                  required
                />
              </div>
              <p className="text-xs text-muted-foreground">Used to sign in alongside your username.</p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Password *</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type={showPw ? "text" : "password"}
                  placeholder="Min. 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-12 pr-12 h-12 bg-card"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPw ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Confirm Password *</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type={showPw ? "text" : "password"}
                  placeholder="Repeat your password"
                  value={confirmPw}
                  onChange={(e) => setConfirmPw(e.target.value)}
                  className="pl-12 h-12 bg-card"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 rounded-md bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white font-medium text-base flex items-center justify-center gap-2 transition-colors"
            >
              {loading ? "Signing up…" : <> Sign Up <ArrowRight className="w-5 h-5" /> </>}
            </button>
          </form>

          <p className="text-center mt-8 text-muted-foreground text-sm">
            Already have an account?{" "}
            <Link
              to={`/login${searchParams.get("redirect") ? `?redirect=${searchParams.get("redirect")}` : ""}`}
              className="text-emerald-600 font-medium hover:text-emerald-500 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;
