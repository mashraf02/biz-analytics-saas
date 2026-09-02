import { useEffect, useState } from "react";
import api from "../api/client";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [cost, setCost] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const res = await api.get("/products");
      setProducts(res.data);
    } catch (err) {
      setError("Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/products", {
        name,
        price: parseFloat(price),
        cost: cost ? parseFloat(cost) : null,
      });
      setName("");
      setPrice("");
      setCost("");
      await loadProducts();
    } catch (err) {
      setError("Failed to add product");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Products</h1>

      <form onSubmit={handleAdd} className="bg-slate-800 rounded-xl p-5 mb-6 flex flex-wrap gap-3 items-end">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Name</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="rounded-lg bg-slate-700 text-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Price (৳)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
            className="rounded-lg bg-slate-700 text-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-emerald-500 w-28"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Cost (৳, optional)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={cost}
            onChange={(e) => setCost(e.target.value)}
            className="rounded-lg bg-slate-700 text-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-emerald-500 w-28"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition"
        >
          {submitting ? "Adding..." : "Add Product"}
        </button>
      </form>

      {error && <p className="text-red-400 mb-4">{error}</p>}
      {loading ? (
        <p className="text-slate-400">Loading...</p>
      ) : products.length === 0 ? (
        <p className="text-slate-400">No products yet.</p>
      ) : (
        <div className="bg-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-700 text-slate-300">
              <tr>
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Price</th>
                <th className="text-left px-4 py-3">Cost</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id} className="border-t border-slate-700">
                  <td className="px-4 py-3">{p.name}</td>
                  <td className="px-4 py-3">৳{p.price}</td>
                  <td className="px-4 py-3 text-slate-400">{p.cost ? `৳${p.cost}` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
