class ReportService:

    @staticmethod
    def build_whatsapp_report(batch, simulation: dict) -> str:
        econ = simulation["economics"]
        stats = simulation["statistics"]

        lines = [
            "🍌 *BANANA INSPECTION REPORT*",
            "",
            f"Samples analyzed: {len(batch)}",
            "",
            f"📏 Avg Length: {stats['length']['mean']} cm (±{stats['length']['std']})",
            f"⚖️ Avg Weight: {stats['weight']['mean']} g",
            f"⭐ Avg Quality: {stats['quality']['mean']}",
            "",
            f"📦 Simulated Shipment: {simulation['quantity']} bananas",
            f"🚚 Total Weight: {econ['total_weight_kg']} kg",
            f"⏳ Est. Shelf Life: {simulation['estimated_shelf_life_days']} days",
            "",
            "💰 *Economics*",
            f"• Revenue: ${econ['estimated_revenue']}",
            f"• Logistics: ${econ['logistics_cost']}",
            f"• Expected Loss ({econ['loss_pct']}%): ${econ['estimated_loss']}",
            f"• *Net Profit*: ${econ['net_profit']}",
            "",
            "🍃 Ripeness Distribution:"
        ]

        for r, c in simulation["ripeness_distribution"].items():
            lines.append(f"- {r}: {c}")

        lines.append("\n— Automated Vision System")

        return "\n".join(lines)
