import * as React from "react";
import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Mail, Lock, Eye, EyeOff, ArrowRight, AlertCircle, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import SparkleIcon from "@/components/SparkleIcon";
import { loginUser } from "@/api/chatApi";
import { useAuth } from "@/hooks/use-auth";

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

const Login = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/";
  const registered = searchParams.get("registered") === "1";
  const { login } = useAuth();

  const [identifier, setIdentifier] = useState("");
  const [password, setPassword]     = useState("");
  const [showPw, setShowPw]         = useState(false);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { access_token, user } = await loginUser(identifier, password);
      login(user, access_token);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      let msg = err.message || "Invalid credentials.";
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
            Evidence-Based<br />
            <span className="text-emerald-400">Medical Intelligence</span>
          </h1>
          <p className="text-white/70 text-lg max-w-md text-center">
            Access reliable clinical information powered by GraphRAG — backed by peer-reviewed research.
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
            <h2 className="text-2xl font-bold text-foreground mb-1">Sign in</h2>
            <p className="text-muted-foreground text-sm">Enter your email and password to continue.</p>
          </div>

          {registered && (
            <div className="mb-5 flex items-center gap-2 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 text-sm">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              Account created successfully. Please sign in.
            </div>
          )}

          {error && (
            <div className="mb-5 flex items-center gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Email</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type="email"
                  placeholder="dr@hospital.com"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  className="pl-12 h-12 bg-card"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type={showPw ? "text" : "password"}
                  placeholder="••••••••"
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

            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 rounded-md bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white font-medium text-base flex items-center justify-center gap-2 transition-colors"
            >
              {loading ? "Signing in…" : (
                <>Sign In <ArrowRight className="w-5 h-5" /></>
              )}
            </button>
          </form>

          <p className="text-center mt-8 text-muted-foreground text-sm">
            Don't have an account?{" "}
            <Link
              to={`/signup${searchParams.get("redirect") ? `?redirect=${searchParams.get("redirect")}` : ""}`}
              className="text-emerald-600 font-medium hover:text-emerald-500 transition-colors"
            >
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
