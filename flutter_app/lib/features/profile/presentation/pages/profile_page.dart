import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../auth/presentation/bloc/auth_bloc.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Profile')),
      body: BlocBuilder<AuthBloc, AuthState>(
        builder: (context, state) {
          if (state is AuthAuthenticated) {
            final user = state.user;
            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // Avatar
                  const CircleAvatar(
                    radius: 50,
                    backgroundColor: AppTheme.primaryColor,
                    child: Icon(Icons.person, size: 50, color: Colors.white),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    user.name,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(user.email,
                      style: const TextStyle(color: Colors.grey)),
                  const SizedBox(height: 24),

                  // Loyalty card
                  Card(
                    color: AppTheme.primaryColor,
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Row(
                        children: [
                          const Icon(Icons.star, color: Colors.white, size: 40),
                          const SizedBox(width: 16),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '${user.loyaltyPoints} Points',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                '${user.loyaltyTier.toUpperCase()} Member',
                                style: const TextStyle(color: Colors.white70),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Referral code
                  if (user.referralCode.isNotEmpty)
                    Card(
                      child: ListTile(
                        leading: const Icon(Icons.share,
                            color: AppTheme.primaryColor),
                        title: const Text('Your Referral Code'),
                        subtitle: Text(user.referralCode),
                        trailing: IconButton(
                          icon: const Icon(Icons.copy),
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Referral code copied!'),
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                  const SizedBox(height: 16),

                  // Info cards
                  _buildInfoCard('Phone', user.phone.isEmpty ? 'Not set' : user.phone,
                      Icons.phone),
                  _buildInfoCard('Skin Type',
                      user.skinType.isEmpty ? 'Not set' : user.skinType, Icons.face),
                ],
              ),
            );
          }
          return const Center(child: Text('Please sign in'));
        },
      ),
    );
  }

  Widget _buildInfoCard(String label, String value, IconData icon) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: AppTheme.primaryColor),
        title: Text(label),
        subtitle: Text(value),
        trailing: const Icon(Icons.edit_outlined, size: 18),
      ),
    );
  }
}
