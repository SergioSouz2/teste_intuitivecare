import { defineStore } from "pinia";
import axios from "axios";

export const useOperadorasStore = defineStore("operadoras", {
  state: () => ({
    operadoras: [],
    total: 0,
    page: 1,
    limit: 10,
    search: "",
    loading: false,
    estatisticas: null,
    despesasUF: [],
  }),
  actions: {
    async fetchOperadoras() {
      this.loading = true;
      try {
        const res = await axios.get("http://localhost:8000/api/operadoras/", {
          params: {
            page: this.page,
            limit: this.limit,
            search: this.search,
          },
        });
        this.operadoras = res.data.data;
        this.total = res.data.total;
      } catch (err) {
        alert("Erro ao carregar operadoras");
      } finally {
        this.loading = false;
      }
    },

    async fetchEstatisticas() {
      try {
        const res = await axios.get("http://localhost:8000/api/estatisticas/");
        this.estatisticas = res.data;

        if (res.data.top5_operadoras) {
          this.despesasUF = res.data.top5_operadoras.map(op => ({
            uf: op.razao_social,
            valor: op.total
          }));
        }
      } catch (err) {
        alert("Erro ao carregar estatísticas");
      }
    },

    async fetchDespesas(cnpj) {
      try {
        const res = await axios.get(`http://localhost:8000/api/operadoras/${cnpj}/despesas/`);
        return res.data;
      } catch (err) {
        alert("Erro ao carregar histórico de despesas");
        return [];
      }
    }
  }
});
