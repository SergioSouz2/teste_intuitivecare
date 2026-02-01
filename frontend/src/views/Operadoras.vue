<template>
  <div class="operadoras-container">
    <h1>Operadoras</h1>

    <!-- FILTROS -->
    <div class="filtros">
      <!-- Razão Social -->
      <select v-model="filtroRazao" @change="onSearch">
        <option value="">Todas as Razões Sociais</option>
        <option v-for="razao in opcoesRazao" :key="razao" :value="razao">
          {{ razao }}
        </option>
      </select>

      <!-- UF -->
      <select v-model="filtroUf" @change="onSearch">
        <option value="">Todos os Estados</option>
        <option v-for="uf in opcoesUf" :key="uf" :value="uf">
          {{ uf }}
        </option>
      </select>

      <!-- CNPJ com máscara -->
      <input
        v-model="search"
        @input="formatarCNPJ"
        @keyup.enter="onSearch"
        placeholder="Buscar por CNPJ"
      />

      <button @click="onSearch" class="btn-search">
        <i class="fa-solid fa-magnifying-glass"></i>
        Buscar
      </button>
    </div>

    <!-- TABELA -->
    <table v-if="!loading && operadoras.length">
      <thead>
        <tr>
          <th>CNPJ</th>
          <th>Razão Social</th>
          <th>UF</th>
          <th>Cidade</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="op in operadoras" :key="String(op.id)">
          <td>{{ formatCNPJ(op.cnpj) }}</td>
          <td>{{ op.razao_social }}</td>
          <td>{{ op.uf }}</td>
          <td>{{ op.cidade }}</td>
          <td>
            <router-link
              :to="`/detalhes/${op.cnpj.replace(/\D/g, '')}`"
              class="btn-ver"
              title="Ver detalhes"
            >
              <i class="fas fa-eye"></i>
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- LOADING -->
    <p v-if="loading" class="info">Carregando...</p>

    <!-- EMPTY -->
    <p v-if="!loading && !operadoras.length" class="info">
      Nenhuma operadora encontrada
    </p>

    <!-- PAGINAÇÃO -->
    <div v-if="operadoras.length" class="paginacao">
      <button @click="prevPage" :disabled="page === 1">
        <i class="fa-solid fa-chevron-left"></i>
      </button>

      <span>Página {{ page }} de {{ totalPages }}</span>

      <button @click="nextPage" :disabled="page === totalPages">
        <i class="fa-solid fa-chevron-right"></i>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import axios from "axios";

export default {
  name: "Operadoras",
  setup() {
    const operadoras = ref([]);
    const opcoesRazao = ref([]);
    const opcoesUf = ref([]);
    const filtroRazao = ref("");
    const filtroUf = ref("");
    const search = ref("");
    const page = ref(1);
    const limit = ref(10);
    const total = ref(0);
    const loading = ref(false);

    const totalPages = computed(() => Math.ceil(total.value / limit.value));

    // 🔹 Formata o CNPJ
    const formatCNPJ = (cnpj) => {
      if (!cnpj) return "";
      cnpj = cnpj.replace(/\D/g, "").substring(0, 14);
      if (cnpj.length > 12)
        return cnpj.replace(
          /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{0,2})$/,
          "$1.$2.$3/$4-$5"
        );
      else if (cnpj.length > 8)
        return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{0,4})$/, "$1.$2.$3/$4");
      else if (cnpj.length > 5)
        return cnpj.replace(/^(\d{2})(\d{3})(\d{0,3})$/, "$1.$2.$3");
      else if (cnpj.length > 2) return cnpj.replace(/^(\d{2})(\d{0,3})$/, "$1.$2");
      return cnpj;
    };

    const formatarCNPJ = () => {
      search.value = formatCNPJ(search.value);
    };

    // 🔹 Carrega filtros
    const carregarFiltros = async () => {
      try {
        const [razoes, ufs] = await Promise.all([
          axios.get("http://localhost:8000/api/operadoras/razao_social"),
          axios.get("http://localhost:8000/api/operadoras/ufs"),
        ]);
        opcoesRazao.value = razoes.data.sort((a, b) => a.localeCompare(b));
        opcoesUf.value = ufs.data.sort();
      } catch (err) {
        console.error("Erro ao carregar filtros:", err);
      }
    };

    // 🔹 Carrega operadoras
    const carregarOperadoras = async () => {
      loading.value = true;
      try {
        const { data } = await axios.get("http://localhost:8000/api/operadoras/", {
          params: {
            page: page.value,
            limit: limit.value,
            search: search.value.replace(/\D/g, "") || null,
            razao_social: filtroRazao.value || null,
            uf: filtroUf.value || null,
          },
        });

        operadoras.value = data.data;
        total.value = data.total;
      } catch (error) {
        console.error(error);
        alert("Erro ao carregar operadoras");
      } finally {
        loading.value = false;
      }
    };

    const onSearch = () => {
      page.value = 1;
      carregarOperadoras();
    };

    const nextPage = () => {
      if (page.value < totalPages.value) {
        page.value++;
        carregarOperadoras();
      }
    };

    const prevPage = () => {
      if (page.value > 1) {
        page.value--;
        carregarOperadoras();
      }
    };

    onMounted(() => {
      carregarFiltros();
      carregarOperadoras();
    });

    return {
      operadoras,
      opcoesRazao,
      opcoesUf,
      filtroRazao,
      filtroUf,
      search,
      page,
      totalPages,
      loading,
      onSearch,
      nextPage,
      prevPage,
      formatarCNPJ,
      formatCNPJ,
    };
  },
};
</script>

<style scoped>
.operadoras-container {
  padding: 20px;
  overflow-y: auto;
}

.filtros {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

select,
input {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

select {
  width: 250px;
}

input {
  width: 200px;
}

.btn-search {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  border-radius: 6px;
  border: none;
  background: #9b59d8;
  color: white;
  cursor: pointer;
  transition: 0.3s;
}

.btn-search:hover {
  background: #7d3cb3;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid #eee;
  font-size: small;
}

thead {
  background: #9b59d8;
  color: white;
}

tbody tr:hover {
  background: #f4ecfb;
}

.btn-ver {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #9b59d8;
  color: white;
  border-radius: 50%;
  text-decoration: none;
  transition: 0.3s;
}

.btn-ver:hover {
  background: #7d3cb3;
  transform: scale(1.1);
}

.info {
  margin-top: 20px;
  text-align: center;
  color: #555;
}

.paginacao {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 12px;
  align-items: center;
}

.paginacao button {
  background: #9b59d8;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
}

.paginacao button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
