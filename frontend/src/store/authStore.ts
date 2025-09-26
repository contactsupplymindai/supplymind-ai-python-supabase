import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@supabase/supabase-js';
import { auth } from '../lib/supabase';
import toast from 'react-hot-toast';

// Auth Store Interface
interface AuthState {
  // State
  user: User | null;
  loading: boolean;
  initialized: boolean;
  
  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setInitialized: (initialized: boolean) => void;
  signUp: (email: string, password: string, userData?: any) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  clearError: () => void;
}

// Create Zustand Auth Store
export const useAuthStore = create<AuthState>()(n  persist(
    (set, get) => ({
      // Initial State
      user: null,
      loading: false,
      initialized: false,

      // Actions
      setUser: (user) => {
        set({ user });
      },

      setLoading: (loading) => {
        set({ loading });
      },

      setInitialized: (initialized) => {
        set({ initialized });
      },

      // Sign Up Function
      signUp: async (email, password, userData) => {
        try {
          set({ loading: true });
          
          const { data, error } = await auth.signUp(email, password, userData);
          
          if (error) {
            toast.error(error.message || 'Failed to create account');
            throw error;
          }
          
          if (data.user) {
            set({ user: data.user });
            toast.success('Account created successfully! Please check your email to verify your account.');
          }
        } catch (error: any) {
          console.error('Sign up error:', error);
          toast.error(error.message || 'Failed to create account');
          throw error;
        } finally {
          set({ loading: false });
        }
      },

      // Sign In Function
      signIn: async (email, password) => {
        try {
          set({ loading: true });
          
          const { data, error } = await auth.signIn(email, password);
          
          if (error) {
            toast.error(error.message || 'Failed to sign in');
            throw error;
          }
          
          if (data.user) {
            set({ user: data.user });
            toast.success('Signed in successfully!');
          }
        } catch (error: any) {
          console.error('Sign in error:', error);
          toast.error(error.message || 'Failed to sign in');
          throw error;
        } finally {
          set({ loading: false });
        }
      },

      // Sign Out Function
      signOut: async () => {
        try {
          set({ loading: true });
          
          const { error } = await auth.signOut();
          
          if (error) {
            toast.error(error.message || 'Failed to sign out');
            throw error;
          }
          
          set({ user: null });
          toast.success('Signed out successfully!');
        } catch (error: any) {
          console.error('Sign out error:', error);
          toast.error(error.message || 'Failed to sign out');
          throw error;
        } finally {
          set({ loading: false });
        }
      },

      // Reset Password Function
      resetPassword: async (email) => {
        try {
          set({ loading: true });
          
          const { data, error } = await auth.resetPassword(email);
          
          if (error) {
            toast.error(error.message || 'Failed to send reset email');
            throw error;
          }
          
          toast.success('Password reset email sent! Please check your inbox.');
        } catch (error: any) {
          console.error('Reset password error:', error);
          toast.error(error.message || 'Failed to send reset email');
          throw error;
        } finally {
          set({ loading: false });
        }
      },

      // Clear Error Function (for future error state)
      clearError: () => {
        // Reserved for future error state management
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        initialized: state.initialized,
      }),
    }
  )
);

// Auth Store Selectors (for optimized re-renders)
export const useUser = () => useAuthStore((state) => state.user);
export const useLoading = () => useAuthStore((state) => state.loading);
export const useInitialized = () => useAuthStore((state) => state.initialized);

// Auth Actions Selectors
export const useAuthActions = () => useAuthStore((state) => ({
  setUser: state.setUser,
  setLoading: state.setLoading,
  setInitialized: state.setInitialized,
  signUp: state.signUp,
  signIn: state.signIn,
  signOut: state.signOut,
  resetPassword: state.resetPassword,
  clearError: state.clearError,
}));

// Auth Computed Values
export const useIsAuthenticated = () => {
  const user = useUser();
  const initialized = useInitialized();
  return { isAuthenticated: !!user, initialized };
};

// Export default store
export default useAuthStore;
