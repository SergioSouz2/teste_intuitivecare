<template>
  <div class="page-container">
    <div class="card">
      <h2 class="card-title">{{ operadora.razao_social }}</h2>
      <p><strong>CNPJ:</strong> {{ operadora.cnpj }}</p>
      <p><strong>UF:</strong> {{ operadora.uf }}</p>
      <p><strong>Cidade:</strong> {{ operadora.cidade }}</p>

      <h3 class="sub-title">Histórico de Despesas</h3>
      <table v-if="despesas.length">
        <thead>
          <tr>
            <th>Ano</th>
            <th>Trimestre</th>
            <th>Valor</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in despesas" :key="d.ano + '-' + d.trimestre">
            <td>{{ d.ano }}</td>
            <td>{{ d.trimestre }}</td>
            <td>{{ d.valor_despesas.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">Carregando ou sem despesas</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useOperadorasStore } from "../store/operadoras";

export default {
  setup() {
    const route = useRoute();
    const store = useOperadorasStore();
    const operadora = ref({});
    const despesas = ref([]);

    const fetchData = async () => {
      try {
        const cnpj = route.params.cnpj;
        const res = await fetch(`http://localhost:8000/api/operadoras/${cnpj}/`);
        operadora.value = await res.json();
        despesas.value = await store.fetchDespesas(cnpj);
      } catch (err) {
        alert("Erro ao carregar detalhes da operadora");
      }
    };

    onMounted(fetchData);

    return { operadora, despesas };
  }
};
</script>

<style scoped>
.page-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 40px 20px;
  background-color: #f5f5f5;
}

.card {
  background-color: #fff;
  padding: 30px 40px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-width: 700px;
  width: 100%;
  transition: transform 0.3s;
}

.card:hover {
  transform: translateY(-5px);
}

.card-title {
  font-size: 1.8rem;
  margin-bottom: 15px;
  color: #9b59d8;
}

.sub-title {
  font-size: 1.3rem;
  margin-top: 25px;
  margin-bottom: 10px;
  color: #333;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

thead {
  background-color: #9b59d8;
  color: #fff;
  font-weight: 500;
}

tbody tr:hover {
  background-color: #f9f3fd;
}

.empty {
  text-align: center;
  color: #555;
  margin-top: 15px;
  font-style: italic;
}
</style>
