import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

function StatCard({ label, value }) {
  return (
    <div className="bg-slate-800 rounded-xl p-5">
      <p className="text-slate-400 text-sm">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
    </div>
  );
}

export default function Dashboard() {
  const { logout } = useAuth();
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const [summaryRes, trendRes] = await Promise.all([
          api.get("/analytics/summary"),
          api.get("/analytics/revenue-trend"),
        ]);
        setSummary(summaryRes.data);
        setTrend(trendRes.data);
      } catch (err) {
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={logout}
          className="text-sm text-slate-400 hover:text-white transition"
        >
          Log out
        </button>
      </div>

      {loading && <p className="text-slate-400">Loading...</p>}
      {error && <p className="text-red-400">{error}</p>}

      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <StatCard label="Total Revenue" value={`৳${summary.total_revenue}`} />
          <StatCard label="Total Orders" value={summary.total_orders} />
          <StatCard label="Average Order Value" value={`৳${summary.average_order_value}`} />
        </div>
      )}

      <div className="bg-slate-800 rounded-xl p-5">
        <h2 className="text-lg font-semibold mb-4">Revenue Trend</h2>
        {trend.length === 0 ? (
          <p className="text-slate-400 text-sm">No order history yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="day" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ backgroundColor: "#1e293b", border: "none" }}
              />
              <Line type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
