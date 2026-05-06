import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      selectedAccountId: null,           // persisted selected account
      setAuth: (token, user) => set({ token, user }),
      setSelectedAccount: (id) => set({ selectedAccountId: id }),
      logout: () => set({ token: null, user: null, selectedAccountId: null }),
    }),
    {
      name: 'auth-storage',
    }
  )
);

export default useAuthStore;
