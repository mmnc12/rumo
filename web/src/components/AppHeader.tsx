import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { NotificationBell } from "./NotificationBell";

export function AppHeader() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();

  // Fecha o drawer com Esc (acessibilidade + conveniência)
  useEffect(() => {
    if (!menuOpen) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setMenuOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  // Trava o scroll do body enquanto o drawer está aberto (mobile)
  useEffect(() => {
    if (!menuOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [menuOpen]);

  function closeMenu() {
    setMenuOpen(false);
  }

  function goToSearch(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const q = String(fd.get("q") ?? "").trim();
    navigate(q ? `/search?q=${encodeURIComponent(q)}` : "/search");
  }

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-4">
          <Link
            to="/activities"
            className="text-lg font-semibold text-rumo-600 hover:text-rumo-700"
          >
            Rumo
          </Link>

          {/* Nav desktop — inalterado */}
          <nav className="hidden items-center gap-3 sm:flex">
            <NavLink
              to="/feed"
              className={({ isActive }) =>
                `text-sm font-medium transition ${
                  isActive
                    ? "text-rumo-600"
                    : "text-gray-600 hover:text-gray-900"
                }`
              }
            >
              Feed
            </NavLink>
            <NavLink
              to="/activities"
              className={({ isActive }) =>
                `text-sm font-medium transition ${
                  isActive
                    ? "text-rumo-600"
                    : "text-gray-600 hover:text-gray-900"
                }`
              }
            >
              Minhas atividades
            </NavLink>
          </nav>
        </div>

        {/* Ações desktop — busca, sino, username */}
        <div className="hidden items-center gap-3 sm:flex">
          <form onSubmit={goToSearch} role="search">
            <input
              type="search"
              name="q"
              placeholder="Buscar usuários…"
              aria-label="Buscar usuários"
              className="w-40 rounded-lg border border-gray-300 px-3 py-1.5 text-sm outline-none focus:border-rumo-500 focus:ring-2 focus:ring-rumo-100"
            />
          </form>

          <Link
            to="/upload"
            className="rounded-lg bg-rumo-500 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-rumo-600"
          >
            + Enviar
          </Link>

          {user && <NotificationBell />}

          {user && (
            <Link
              to={`/users/${user.id}`}
              className="text-sm text-gray-500 hover:text-gray-900"
            >
              {user.username}
            </Link>
          )}

          <button
            type="button"
            onClick={logout}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          >
            Sair
          </button>
        </div>

        {/* Hamburger mobile */}
        <button
          type="button"
          onClick={() => setMenuOpen(true)}
          className="inline-flex items-center justify-center rounded-lg p-2 text-gray-700 hover:bg-gray-100 sm:hidden"
          aria-label="Abrir menu"
          aria-expanded={menuOpen}
          aria-controls="mobile-drawer"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
      </div>

      {/* Drawer mobile */}
      {menuOpen && (
        <div
          className="fixed inset-0 z-50 sm:hidden"
          role="dialog"
          aria-modal="true"
          id="mobile-drawer"
        >
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/40"
            onClick={closeMenu}
            aria-hidden="true"
          />

          {/* Painel */}
          <div className="absolute left-0 top-0 h-full w-72 max-w-[80%] bg-white shadow-xl">
            <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
              <span className="text-lg font-semibold text-rumo-600">Rumo</span>
              <div className="flex items-center gap-1">
                {/* Sino visível no topo do drawer (badge sempre visível) */}
                {user && <NotificationBell />}
                <button
                  type="button"
                  onClick={closeMenu}
                  className="rounded-lg p-2 text-gray-500 hover:bg-gray-100"
                  aria-label="Fechar menu"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <nav className="flex flex-col p-2">
              <DrawerLink to="/feed" onClick={closeMenu}>
                Feed
              </DrawerLink>
              <DrawerLink to="/activities" onClick={closeMenu}>
                Minhas atividades
              </DrawerLink>
              <DrawerLink to="/search" onClick={closeMenu}>
                Buscar usuários
              </DrawerLink>
              <DrawerLink to="/notifications" onClick={closeMenu}>
                Notificações
              </DrawerLink>
              <DrawerLink to="/upload" onClick={closeMenu}>
                + Enviar atividade
              </DrawerLink>
              {user && (
                <DrawerLink to={`/users/${user.id}`} onClick={closeMenu}>
                  Perfil (@{user.username})
                </DrawerLink>
              )}
            </nav>

            <div className="border-t border-gray-200 p-2">
              <button
                type="button"
                onClick={() => {
                  closeMenu();
                  logout();
                }}
                className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 hover:bg-red-50"
              >
                Sair
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

function DrawerLink({
  to,
  onClick,
  children,
}: {
  to: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        `rounded-lg px-3 py-2 text-sm font-medium transition ${
          isActive
            ? "bg-rumo-50 text-rumo-600"
            : "text-gray-700 hover:bg-gray-100"
        }`
      }
    >
      {children}
    </NavLink>
  );
}