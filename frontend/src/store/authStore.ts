import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';
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
  initialize: () => Promise<void>; // ADDED MISSING METHOD
  signUp: (email: string, password: string, userData?: any) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  clearError: () => void;
}

// Create Zustand Auth Store
export const useAuthStore = create<AuthState>()(
  persist(
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

      // ADDED MISSING INITIALIZE METHOD
      initialize: async () => {
        const state = get();
        if (state.initialized) return;

        set({ loading: true });
        
        try {
          const { data: { session } } = await supabase.auth.getSession();
          if (session?.user) {
            set({ user: session.user });
          }
        } catch (error) {
          console.error('Error initializing auth:', error);
        } finally {
          set({ loading: false, initialized: true });
        }
      },

      signUp: async (email, password, userData) => {
        set({ loading: true });
        try {
          const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
              data: userData,
            },
          });

          if (error) {
            toast.error(error.message);
            return;
          }

          if (data.user) {
            toast.success('Account created successfully! Please check your email for verification.');
            set({ user: data.user });
          }
        } catch (error: any) {
          toast.error('An unexpected error occurred');
        } finally {
          set({ loading: false });
        }
      },

      signIn: async (email, password) => {
        set({ loading: true });
        try {
          const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password,
          });

          if (error) {
            toast.error(error.message);
            return;
          }

          if (data.user) {
            toast.success('Welcome back!');
            set({ user: data.user });
          }
        } catch (error: any) {
          toast.error('An unexpected error occurred');
        } finally {
          set({ loading: false });
        }
      },

      signOut: async () => {
        set({ loading: true });
        try {
          const { error } = await supabase.auth.signOut();
          if (error) {
            toast.error(error.message);
            return;
          }
          
          set({ user: null });
          toast.success('Signed out successfully');
        } catch (error: any) {
          toast.error('An unexpected error occurred');
        } finally {
          set({ loading: false });
        }
      },

      resetPassword: async (email) => {
        set({ loading: true });
        try {
          const { error } = await supabase.auth.resetPasswordForEmail(email);
          if (error) {
            toast.error(error.message);
            return;
          }
          
          toast.success('Password reset email sent!');
        } catch (error: any) {
          toast.error('An unexpected error occurred');
        } finally {
          set({ loading: false });
        }
      },

      clearError: () => {
        // Clear any error state if needed
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user }),
    }
  )
);
