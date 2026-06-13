import { useNavigate } from "react-router-dom";
import SparkleIcon from "@/components/SparkleIcon";

const NotAuthorized = () => {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center space-y-6 px-6">
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-xl bg-emerald-500 flex items-center justify-center">
            <SparkleIcon className="w-9 h-9 text-white" />
          </div>
        </div>

        <div>
          <h1 className="text-6xl font-bold text-foreground mb-2">403</h1>
          <p className="text-xl font-semibold text-foreground">Access Denied</p>
          <p className="text-muted-foreground mt-2 max-w-sm mx-auto">
            This conversation doesn't belong to your account. You can only view your own chats.
          </p>
        </div>

        <button
          onClick={() => navigate("/", { replace: true })}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white font-medium transition-colors"
        >
          Go to my chats
        </button>
      </div>
    </div>
  );
};

export default NotAuthorized;
