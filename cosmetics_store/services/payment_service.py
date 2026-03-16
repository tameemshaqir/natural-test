import logging
import json

_logger = logging.getLogger(__name__)


class PaymentService:
    """Service for handling PayPal payment integration."""

    @staticmethod
    def create_paypal_payment(order, return_url, cancel_url):
        """Create a PayPal payment for an order.

        In production, this would integrate with PayPal REST API.
        Requires PayPal client ID and secret in system parameters.

        Args:
            order: sale.order record
            return_url: URL to redirect after successful payment
            cancel_url: URL to redirect after cancelled payment

        Returns:
            dict with payment_id and approval_url
        """
        config = order.env['ir.config_parameter'].sudo()
        client_id = config.get_param('cosmetics_store.paypal_client_id', '')
        mode = config.get_param('cosmetics_store.paypal_mode', 'sandbox')

        if not client_id:
            _logger.warning("PayPal client ID not configured")
            return {'error': 'Payment gateway not configured'}

        # PayPal API integration placeholder
        # In production, use the paypalrestsdk or requests library
        payment_data = {
            'intent': 'sale',
            'payer': {'payment_method': 'paypal'},
            'transactions': [{
                'amount': {
                    'total': str(order.amount_total),
                    'currency': order.currency_id.name or 'USD',
                },
                'description': f'Order {order.name}',
            }],
            'redirect_urls': {
                'return_url': return_url,
                'cancel_url': cancel_url,
            },
        }

        _logger.info("PayPal payment created for order %s: %s",
                      order.name, json.dumps(payment_data))

        return {
            'payment_id': f'PAYPAL-{order.id}',
            'approval_url': f'https://www.sandbox.paypal.com/checkoutnow?token=MOCK-{order.id}',
            'mode': mode,
        }

    @staticmethod
    def execute_paypal_payment(order, payment_id, payer_id):
        """Execute (capture) a PayPal payment after customer approval.

        Args:
            order: sale.order record
            payment_id: PayPal payment ID
            payer_id: PayPal payer ID

        Returns:
            dict with success status
        """
        _logger.info(
            "Executing PayPal payment %s for order %s (payer: %s)",
            payment_id, order.name, payer_id
        )

        # In production, verify and execute payment with PayPal API
        order.sudo().write({
            'payment_status': 'paid',
            'payment_reference': payment_id,
            'payment_method': 'paypal',
        })

        return {
            'success': True,
            'payment_id': payment_id,
            'status': 'completed',
        }

    @staticmethod
    def refund_paypal_payment(order, amount=None):
        """Refund a PayPal payment.

        Args:
            order: sale.order record
            amount: Amount to refund (None = full refund)

        Returns:
            dict with refund status
        """
        refund_amount = amount or order.amount_total

        _logger.info(
            "Refunding PayPal payment for order %s, amount: %s",
            order.name, refund_amount
        )

        order.sudo().write({
            'payment_status': 'refunded',
        })

        return {
            'success': True,
            'refund_amount': refund_amount,
        }
