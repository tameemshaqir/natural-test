import logging
import json

_logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending push notifications via Firebase Cloud Messaging."""

    FCM_URL = 'https://fcm.googleapis.com/fcm/send'

    @staticmethod
    def send_push_notification(env, partner_id, title, body, data=None):
        """Send push notification to a customer's device.

        Args:
            env: Odoo environment
            partner_id: res.partner ID
            title: Notification title
            body: Notification body text
            data: Additional data payload (dict)

        Returns:
            bool: Success status
        """
        partner = env['res.partner'].sudo().browse(partner_id)
        if not partner.exists() or not partner.firebase_token:
            _logger.info("No Firebase token for partner %s", partner_id)
            return False

        server_key = env['ir.config_parameter'].sudo().get_param(
            'cosmetics_store.firebase_server_key', ''
        )
        if not server_key:
            _logger.warning("Firebase server key not configured")
            return False

        payload = {
            'to': partner.firebase_token,
            'notification': {
                'title': title,
                'body': body,
                'sound': 'default',
                'click_action': 'FLUTTER_NOTIFICATION_CLICK',
            },
            'data': data or {},
        }

        _logger.info(
            "Sending push notification to partner %s: %s",
            partner_id, json.dumps(payload)
        )

        # In production, use requests library to send to FCM
        # headers = {
        #     'Authorization': f'key={server_key}',
        #     'Content-Type': 'application/json',
        # }
        # response = requests.post(FCM_URL, json=payload, headers=headers)
        # return response.status_code == 200

        return True

    @staticmethod
    def notify_order_status(env, order):
        """Send notification about order status change.

        Args:
            env: Odoo environment
            order: sale.order record
        """
        status_messages = {
            'confirmed': 'Your order has been confirmed!',
            'processing': 'Your order is being processed.',
            'shipped': f'Your order has been shipped! Tracking: {order.tracking_number or "N/A"}',
            'delivered': 'Your order has been delivered!',
            'cancelled': 'Your order has been cancelled.',
        }

        status = order.order_status
        if status in status_messages:
            NotificationService.send_push_notification(
                env,
                order.partner_id.id,
                f'Order {order.name} Update',
                status_messages[status],
                {
                    'type': 'order_update',
                    'order_id': str(order.id),
                    'status': status,
                },
            )

    @staticmethod
    def notify_subscription_renewal(env, subscription):
        """Notify customer about subscription renewal.

        Args:
            env: Odoo environment
            subscription: cosmetics.subscription record
        """
        NotificationService.send_push_notification(
            env,
            subscription.customer_id.id,
            'Subscription Renewal',
            f'Your {subscription.plan_id.name} subscription has been renewed.',
            {
                'type': 'subscription_renewal',
                'subscription_id': str(subscription.id),
            },
        )

    @staticmethod
    def notify_promotion(env, partner_ids, title, message, promo_data=None):
        """Send promotional notification to multiple customers.

        Args:
            env: Odoo environment
            partner_ids: list of res.partner IDs
            title: Notification title
            message: Notification message
            promo_data: Additional promotion data
        """
        for partner_id in partner_ids:
            NotificationService.send_push_notification(
                env, partner_id, title, message,
                {'type': 'promotion', **(promo_data or {})},
            )
