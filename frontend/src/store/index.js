import { defineStore } from 'pinia';
import axios from 'axios';

export const useOperadoraStore = defineStore('operadora', {
  state: () => ({
    operadoras: [],
    despesas: [],
  }),
  actions: {
    async fetchOperadoras() {
      const response = await axios.get('http://127.0.0.1:8000/api/operadoras');
      this.operadoras = response.data;
    },
    async fetchDespesas(cnpj) {
      const response = await axios.get(`http://127.0.0.1:8000/api/operadoras/${cnpj}/despesas`);
      this.despesas = response.data;
    },
  },
});
