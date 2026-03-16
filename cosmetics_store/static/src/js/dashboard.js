/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class CosmeticsDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            totalOrders: 0,
            totalRevenue: 0,
            totalCustomers: 0,
            totalProducts: 0,
            activeSubscriptions: 0,
            pendingOrders: 0,
            recentOrders: [],
            topProducts: [],
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            // Total orders
            this.state.totalOrders = await this.orm.searchCount("sale.order", [
                ["state", "!=", "draft"],
            ]);

            // Total revenue
            const orders = await this.orm.searchRead(
                "sale.order",
                [["state", "=", "sale"]],
                ["amount_total"]
            );
            this.state.totalRevenue = orders.reduce(
                (sum, o) => sum + o.amount_total,
                0
            );

            // Total customers
            this.state.totalCustomers = await this.orm.searchCount(
                "res.partner",
                [["customer_rank", ">", 0]]
            );

            // Total products
            this.state.totalProducts = await this.orm.searchCount(
                "product.template",
                [["sale_ok", "=", true]]
            );

            // Active subscriptions
            this.state.activeSubscriptions = await this.orm.searchCount(
                "cosmetics.subscription",
                [["status", "=", "active"]]
            );

            // Pending orders
            this.state.pendingOrders = await this.orm.searchCount(
                "sale.order",
                [["order_status", "=", "pending"]]
            );

            // Recent orders
            this.state.recentOrders = await this.orm.searchRead(
                "sale.order",
                [["state", "!=", "draft"]],
                [
                    "name",
                    "partner_id",
                    "amount_total",
                    "order_status",
                    "date_order",
                ],
                { limit: 10, order: "create_date desc" }
            );

            // Top products
            this.state.topProducts = await this.orm.searchRead(
                "product.template",
                [["sale_ok", "=", true]],
                ["name", "list_price", "rating_average", "review_count"],
                { limit: 5, order: "rating_average desc" }
            );
        } catch (error) {
            console.error("Dashboard data loading error:", error);
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
        }).format(amount);
    }

    openOrders() {
        this.action.doAction("sale.action_quotations_with_onboarding");
    }

    openProducts() {
        this.action.doAction("sale.product_template_action");
    }

    openCustomers() {
        this.action.doAction("contacts.action_contacts");
    }

    openSubscriptions() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Subscriptions",
            res_model: "cosmetics.subscription",
            view_mode: "list,form",
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }
}

CosmeticsDashboard.template = "cosmetics_store.Dashboard";

registry.category("actions").add("cosmetics_dashboard", CosmeticsDashboard);
