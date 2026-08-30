import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/customers", label: "Customers" },
  { to: "/products", label: "Products" },
  { to: "/orders", label: "Orders" },
  { to: "/insights", label: "ML Insights" },
];

export default function Layout() {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-900 text-white flex">
      <aside className="w-56 bg-slate-800 p-5 flex flex-col">
        <h2 className="text-lg font-bold mb-8">Biz Analytics</h2>
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm transition ${
                  isActive
                    ? "bg-emerald-500 text-white"
                    : "text-slate-300 hover:bg-slate-700"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <button
          onClick={logout}
          className="mt-auto text-sm text-slate-400 hover:text-white transition text-left"
        >
          Log out
        </button>
      </aside>
      <main className="flex-1 p-8 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
