// Money is handled in paise (whole numbers) so there are no rounding errors in the browser.
export const toPaise = (str) => Math.round(parseFloat(str) * 100);
export const inr = (paise) =>
  "₹" + (paise / 100).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const inrStr = (str) => inr(toPaise(str));

export const STATUS_LABELS = {
  pending: "Pending",
  confirmed: "Confirmed",
  preparing: "Preparing",
  out_for_delivery: "Out for Delivery",
  delivered: "Delivered",
  cancelled: "Cancelled",
};
// Mirrors the backend rules so the admin only sees valid choices (the server still checks).
export const NEXT_STATUS = {
  pending: ["confirmed", "cancelled"],
  confirmed: ["preparing", "cancelled"],
  preparing: ["out_for_delivery", "cancelled"],
  out_for_delivery: ["delivered"],
  delivered: [],
  cancelled: [],
};
export const fmtDate = (iso) =>
  new Date(iso.endsWith("Z") ? iso : iso + "Z").toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
