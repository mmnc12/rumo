import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../api/client";

const loginSchema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(1, "Informe a senha"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (data: LoginForm) => {
    setServerError(null);
    try {
      await login(data);
      const from = (location.state as { from?: string } | null)?.from;
      navigate(from ?? "/activities", { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setServerError(
          typeof err.detail === "string" ? err.detail : "Falha no login"
        );
      } else {
        setServerError("Erro inesperado. Tente novamente.");
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-3xl font-bold text-rumo-500 text-center">Rumo</h1>
        <p className="text-center text-gray-600 mt-1 mb-8">Bora treinar.</p>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="bg-white shadow-sm rounded-lg p-6 space-y-4"
        >
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              autoComplete="email"
              {...register("email")}
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-rumo-500"
              placeholder="teste@rumo.com"
            />
            {errors.email && (
              <p className="text-sm text-red-600 mt-1">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Senha</label>
            <input
              type="password"
              autoComplete="current-password"
              {...register("password")}
              className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-rumo-500"
            />
            {errors.password && (
              <p className="text-sm text-red-600 mt-1">
                {errors.password.message}
              </p>
            )}
          </div>

          {serverError && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded p-2">
              {serverError}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-rumo-500 hover:bg-rumo-600 disabled:opacity-50 text-white font-medium py-2 rounded transition"
          >
            {isSubmitting ? "Entrando…" : "Entrar"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-600 mt-4">
          Não tem conta?{" "}
          <Link to="/register" className="text-rumo-600 hover:underline">
            Criar conta
          </Link>
        </p>
      </div>
    </div>
  );
}