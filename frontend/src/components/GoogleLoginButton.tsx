import { GoogleLogin, type CredentialResponse } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";

interface GoogleLoginButtonProps {
  redirectTo?: string;
}

export function GoogleLoginButton({ redirectTo = "/" }: GoogleLoginButtonProps) {
  const googleLogin = useAuthStore((s) => s.googleLogin);
  const navigate = useNavigate();

  const handleSuccess = async (response: CredentialResponse) => {
    if (!response.credential) return;
    try {
      await googleLogin(response.credential);
      navigate(redirectTo);
    } catch {
      // error handled by store / axios interceptor
    }
  };

  return (
    <GoogleLogin
      onSuccess={handleSuccess}
      onError={() => {
        /* Google popup closed or failed */
      }}
      useOneTap={false}
      theme="outline"
      size="large"
      width={340}
    />
  );
}
