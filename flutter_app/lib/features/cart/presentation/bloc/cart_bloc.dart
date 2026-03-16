import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../../models/cart_item.dart';
import '../../../../services/cart_service.dart';

// Events
abstract class CartEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class CartLoadRequested extends CartEvent {}

class CartItemAdded extends CartEvent {
  final int productId;
  final int quantity;

  CartItemAdded({required this.productId, this.quantity = 1});

  @override
  List<Object?> get props => [productId, quantity];
}

class CartItemUpdated extends CartEvent {
  final int lineId;
  final int quantity;

  CartItemUpdated({required this.lineId, required this.quantity});

  @override
  List<Object?> get props => [lineId, quantity];
}

class CartItemRemoved extends CartEvent {
  final int lineId;

  CartItemRemoved(this.lineId);

  @override
  List<Object?> get props => [lineId];
}

class CartCouponApplied extends CartEvent {
  final String couponCode;

  CartCouponApplied(this.couponCode);

  @override
  List<Object?> get props => [couponCode];
}

// States
abstract class CartState extends Equatable {
  @override
  List<Object?> get props => [];
}

class CartInitial extends CartState {}

class CartLoading extends CartState {}

class CartLoaded extends CartState {
  final Cart cart;

  CartLoaded(this.cart);

  @override
  List<Object?> get props => [cart];
}

class CartError extends CartState {
  final String message;

  CartError(this.message);

  @override
  List<Object?> get props => [message];
}

class CartItemAddedSuccess extends CartState {
  final String message;

  CartItemAddedSuccess(this.message);

  @override
  List<Object?> get props => [message];
}

// Bloc
class CartBloc extends Bloc<CartEvent, CartState> {
  final CartService _cartService;

  CartBloc(this._cartService) : super(CartInitial()) {
    on<CartLoadRequested>(_onLoadRequested);
    on<CartItemAdded>(_onItemAdded);
    on<CartItemUpdated>(_onItemUpdated);
    on<CartItemRemoved>(_onItemRemoved);
    on<CartCouponApplied>(_onCouponApplied);
  }

  Future<void> _onLoadRequested(
    CartLoadRequested event,
    Emitter<CartState> emit,
  ) async {
    emit(CartLoading());
    try {
      final cart = await _cartService.getCart();
      emit(CartLoaded(cart));
    } catch (e) {
      emit(CartError('Failed to load cart.'));
    }
  }

  Future<void> _onItemAdded(
    CartItemAdded event,
    Emitter<CartState> emit,
  ) async {
    try {
      final result = await _cartService.addToCart(
        event.productId,
        quantity: event.quantity,
      );
      if (result['success'] == true) {
        emit(CartItemAddedSuccess(result['message'] ?? 'Added to cart'));
        add(CartLoadRequested());
      } else {
        emit(CartError(result['error'] ?? 'Failed to add to cart'));
      }
    } catch (e) {
      emit(CartError('Failed to add to cart.'));
    }
  }

  Future<void> _onItemUpdated(
    CartItemUpdated event,
    Emitter<CartState> emit,
  ) async {
    try {
      await _cartService.updateCartItem(event.lineId, event.quantity);
      add(CartLoadRequested());
    } catch (e) {
      emit(CartError('Failed to update cart.'));
    }
  }

  Future<void> _onItemRemoved(
    CartItemRemoved event,
    Emitter<CartState> emit,
  ) async {
    try {
      await _cartService.removeFromCart(event.lineId);
      add(CartLoadRequested());
    } catch (e) {
      emit(CartError('Failed to remove item.'));
    }
  }

  Future<void> _onCouponApplied(
    CartCouponApplied event,
    Emitter<CartState> emit,
  ) async {
    try {
      final result = await _cartService.applyCoupon(event.couponCode);
      if (result['success'] == true) {
        add(CartLoadRequested());
      } else {
        emit(CartError(result['error'] ?? 'Invalid coupon'));
      }
    } catch (e) {
      emit(CartError('Failed to apply coupon.'));
    }
  }
}
