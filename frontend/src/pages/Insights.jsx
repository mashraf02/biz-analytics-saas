import { useEffect, useState } from "react";
import api from "../api/client";

function Section({ title, children }) {
  return (
    <div className="bg-slate-800 rounded-xl p-5 mb-6">
      <h2 className="text-lg font-semibold mb-4">{title}</h2>
      {children}
    </div>
  );
}

function NotReliable({ reason }) {
  return (
    <p className="text-slate-400 text-sm bg-slate-700/50 rounded-lg px-4 py-3">
      Not enough data yet. {reason}
    </p>
  );
}

export default function Insights() {
  const [forecast, setForecast] = useState(null);
  const [segments, setSegments] = useState(null);
  const [lowPerformers, setLowPerformers] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadInsights() {
      try {
        const [forecastRes, segmentsRes, lowRes] = await Promise.all([
          api.get("/ml/forecast"),
          api.get("/ml/customer-segments"),
          api.get("/ml/low-performers"),
        ]);
        setForecast(forecastRes.data);
        setSegments(segmentsRes.data);
        setLowPerformers(lowRes.data);
      } catch (err) {
        setError("Failed to load insights");
      } finally {
        setLoading(false);
      }
    }
    loadInsights();
  }, []);

  if (loading) return <p className="text-slate-400">Loading...</p>;
  if (error) return <p className="text-red-400">{error}</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">ML Insights</h1>

      <Section title="Revenue Forecast">
        {forecast.reliable ? (
          <div>
            <p className="text-sm text-slate-400 mb-3">
              Trend: <span className="text-emerald-400 font-medium">{forecast.trend}</span>
            </p>
            <div className="space-y-1">
              {forecast.forecast.map((f) => (
                <div key={f.day} className="flex justify-between text-sm">
                  <span className="text-slate-400">{f.day}</span>
                  <span>৳{f.predicted_revenue}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <NotReliable reason={forecast.reason} />
        )}
      </Section>

      <Section title="Customer Segments">
        {segments.new_customers.length === 0 && segments.repeat_customers.length === 0 ? (
          <p className="text-slate-400 text-sm">No customer order data yet.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-slate-400 mb-2">New ({segments.new_customers.length})</p>
              {segments.new_customers.map((c) => (
                <p key={c.customer_id} className="text-sm py-1">{c.name}</p>
              ))}
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-2">Repeat ({segments.repeat_customers.length})</p>
              {segments.repeat_customers.length === 0 ? (
                <p className="text-sm text-slate-500">None yet</p>
              ) : (
                segments.repeat_customers.map((c) => (
                  <p key={c.customer_id} className="text-sm py-1">{c.name}</p>
                ))
              )}
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-2">High-value ({segments.high_value_customers.length})</p>
              {segments.high_value_customers.length === 0 ? (
                <p className="text-sm text-slate-500">None yet</p>
              ) : (
                segments.high_value_customers.map((c) => (
                  <p key={c.customer_id} className="text-sm py-1">
                    {c.name} — ৳{c.total_spent}
                  </p>
                ))
              )}
            </div>
          </div>
        )}
      </Section>

      <Section title="Low-Performing Products">
        {lowPerformers.reliable ? (
          lowPerformers.low_performers.length === 0 ? (
            <p className="text-slate-400 text-sm">No underperforming products right now — nice work.</p>
          ) : (
            <div className="space-y-1">
              {lowPerformers.low_performers.map((p) => (
                <div key={p.product_id} className="flex justify-between text-sm">
                  <span>{p.name}</span>
                  <span className="text-slate-400">
                    {p.quantity_sold} sold · ৳{p.revenue}
                  </span>
                </div>
              ))}
            </div>
          )
        ) : (
          <NotReliable reason={lowPerformers.reason} />
        )}
      </Section>
    </div>
  );
}
