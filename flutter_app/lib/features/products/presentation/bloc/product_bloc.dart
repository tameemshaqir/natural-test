import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../../models/product.dart';
import '../../../../services/api_service.dart';

// Events
abstract class ProductEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class ProductsFetchRequested extends ProductEvent {
  final int page;
  final String? category;
  final String? skinType;
  final String? sort;

  ProductsFetchRequested({
    this.page = 1,
    this.category,
    this.skinType,
    this.sort,
  });

  @override
  List<Object?> get props => [page, category, skinType, sort];
}

class ProductDetailRequested extends ProductEvent {
  final int productId;

  ProductDetailRequested(this.productId);

  @override
  List<Object?> get props => [productId];
}

class ProductSearchRequested extends ProductEvent {
  final String query;

  ProductSearchRequested(this.query);

  @override
  List<Object?> get props => [query];
}

class TrendingProductsRequested extends ProductEvent {}

// States
abstract class ProductState extends Equatable {
  @override
  List<Object?> get props => [];
}

class ProductInitial extends ProductState {}

class ProductLoading extends ProductState {}

class ProductsLoaded extends ProductState {
  final List<Product> products;
  final int total;
  final int page;
  final bool hasMore;

  ProductsLoaded({
    required this.products,
    this.total = 0,
    this.page = 1,
    this.hasMore = false,
  });

  @override
  List<Object?> get props => [products, total, page, hasMore];
}

class ProductDetailLoaded extends ProductState {
  final Product product;

  ProductDetailLoaded(this.product);

  @override
  List<Object?> get props => [product];
}

class ProductError extends ProductState {
  final String message;

  ProductError(this.message);

  @override
  List<Object?> get props => [message];
}

// Bloc
class ProductBloc extends Bloc<ProductEvent, ProductState> {
  final ApiService _apiService;

  ProductBloc(this._apiService) : super(ProductInitial()) {
    on<ProductsFetchRequested>(_onFetchRequested);
    on<ProductDetailRequested>(_onDetailRequested);
    on<ProductSearchRequested>(_onSearchRequested);
    on<TrendingProductsRequested>(_onTrendingRequested);
  }

  Future<void> _onFetchRequested(
    ProductsFetchRequested event,
    Emitter<ProductState> emit,
  ) async {
    emit(ProductLoading());
    try {
      final data = await _apiService.getProducts(
        page: event.page,
        category: event.category,
        skinType: event.skinType,
        sort: event.sort,
      );
      final products = (data['products'] as List)
          .map((json) => Product.fromJson(json))
          .toList();
      emit(ProductsLoaded(
        products: products,
        total: data['total'] ?? 0,
        page: event.page,
        hasMore: event.page < (data['pages'] ?? 1),
      ));
    } catch (e) {
      emit(ProductError('Failed to load products. Please try again.'));
    }
  }

  Future<void> _onDetailRequested(
    ProductDetailRequested event,
    Emitter<ProductState> emit,
  ) async {
    emit(ProductLoading());
    try {
      final product = await _apiService.getProductDetail(event.productId);
      emit(ProductDetailLoaded(product));
    } catch (e) {
      emit(ProductError('Failed to load product details.'));
    }
  }

  Future<void> _onSearchRequested(
    ProductSearchRequested event,
    Emitter<ProductState> emit,
  ) async {
    emit(ProductLoading());
    try {
      final data = await _apiService.searchProducts(event.query);
      final products = (data['products'] as List)
          .map((json) => Product.fromJson(json))
          .toList();
      emit(ProductsLoaded(
        products: products,
        total: data['total'] ?? 0,
      ));
    } catch (e) {
      emit(ProductError('Search failed. Please try again.'));
    }
  }

  Future<void> _onTrendingRequested(
    TrendingProductsRequested event,
    Emitter<ProductState> emit,
  ) async {
    emit(ProductLoading());
    try {
      final products = await _apiService.getTrending();
      emit(ProductsLoaded(products: products, total: products.length));
    } catch (e) {
      emit(ProductError('Failed to load trending products.'));
    }
  }
}
