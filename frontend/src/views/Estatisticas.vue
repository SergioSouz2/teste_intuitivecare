<template>
  <div class="dashboard-container">
    <h1 class="dashboard-title">Dashboard de Operadoras</h1>

    <!-- FILTRO -->
    <div class="filter-container">
      <label for="filtroUF">Filtrar por UF:</label>
      <select id="filtroUF" v-model="filtroUF" @change="filtrarUF">
        <option value="">Todos</option>
        <option v-for="uf in ufs" :key="uf" :value="uf">{{ uf }}</option>
      </select>
    </div>

    <!-- CARDS -->
    <div class="cards">
      <div class="card">
        <p class="card-label">Total de Despesas</p>
        <p class="card-value">{{ totalDespesas }}</p>
      </div>

      <div class="card">
        <p class="card-label">Média de Despesas</p>
        <p class="card-value">{{ mediaDespesas }}</p>
      </div>

      <div class="card">
        <p class="card-label">Desvio Padrão</p>
        <p class="card-value">{{ desvioPadrao }}</p>
      </div>
    </div>

    <!-- GRÁFICOS -->
    <div class="charts">
      <div class="chart-card">
        <h3>Total de Despesas por UF</h3>
        <canvas ref="totalChart"></canvas>
      </div>

      <div class="chart-card">
        <h3>Média de Despesas por UF</h3>
        <canvas ref="mediaChart"></canvas>
      </div>

      <div class="chart-card">
        <h3>Desvio Padrão por UF</h3>
        <canvas ref="desvioChart"></canvas>
      </div>
    </div>

    <p v-if="loading" class="loading">Carregando dados...</p>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import Chart from "chart.js/auto";
import axios from "axios";

export default {
  setup() {
    const loading = ref(true);
    const filtroUF = ref("");
    const ufs = ref([]);
    const dados = ref([]);

    // Cards
    const totalDespesas = ref("R$ 0,00");
    const mediaDespesas = ref("R$ 0,00");
    const desvioPadrao = ref("R$ 0,00");

    // Canvas refs
    const totalChart = ref(null);
    const mediaChart = ref(null);
    const desvioChart = ref(null);

    let charts = {};

    const filtrarUF = () => {
      renderCharts();
    };

    const renderCharts = () => {
      const dataFiltrada = filtroUF.value
        ? dados.value.filter(d => d.uf === filtroUF.value)
        : dados.value;

      const agrupado = {};
      dataFiltrada.forEach(d => {
        if (!agrupado[d.uf]) agrupado[d.uf] = { total: 0, media: 0, count: 0 };
        agrupado[d.uf].total += d.total_despesas;
        agrupado[d.uf].media += d.media_despesas;
        agrupado[d.uf].count += 1;
      });

      const labels = Object.keys(agrupado);
      const totalData = labels.map(uf => agrupado[uf].total);
      const mediaData = labels.map(uf => agrupado[uf].media / agrupado[uf].count);
      const desvioData = labels.map(uf => {
        const mediaUF = agrupado[uf].media / agrupado[uf].count;
        const variancia = dataFiltrada
          .filter(d => d.uf === uf)
          .reduce((acc, d) => acc + Math.pow(d.total_despesas - mediaUF, 2), 0) / agrupado[uf].count;
        return Math.sqrt(variancia);
      });

      // Função auxiliar para criar chart
      const createChart = (refCanvas, label, data, bgColor) => {
        if (charts[label]) charts[label].destroy();
        charts[label] = new Chart(refCanvas.value, {
          type: "bar",
          data: { labels, datasets: [{ label, data, backgroundColor: bgColor }] },
          options: {
            responsive: true,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: context => context.raw.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: value => value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" }),
                  font: { size: 12 }
                }
              },
              x: { ticks: { font: { size: 12 } } }
            }
          }
        });
      };

      createChart(totalChart, "Total de Despesas", totalData, "#9b59d8");
      createChart(mediaChart, "Média de Despesas", mediaData, "#f39c12");
      createChart(desvioChart, "Desvio Padrão", desvioData, "#e74c3c");
    };

    onMounted(async () => {
      loading.value = true;
      try {
        const { data } = await axios.get("http://localhost:8000/api/estatisticas/");
        dados.value = data;

        ufs.value = [...new Set(data.map(d => d.uf))];

        // Cards
        const total = data.reduce((acc, d) => acc + d.total_despesas, 0);
        const media = data.reduce((acc, d) => acc + d.media_despesas, 0) / data.length;
        const desvio = Math.sqrt(data.reduce((acc, d) => acc + Math.pow(d.total_despesas - media, 2), 0) / data.length);

        totalDespesas.value = total.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
        mediaDespesas.value = media.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
        desvioPadrao.value = desvio.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

        renderCharts();
      } catch (err) {
        console.error("Erro ao buscar estatísticas:", err);
      } finally {
        loading.value = false;
      }
    });

    return {
      loading,
      filtroUF,
      ufs,
      totalDespesas,
      mediaDespesas,
      desvioPadrao,
      totalChart,
      mediaChart,
      desvioChart,
      filtrarUF
    };
  }
};
</script>

<style scoped>
.dashboard-container {
  width: 100vw;
}

.dashboard-title {
  text-align: center;
  font-size: 2.6rem;
  color: #9b59d8;
  margin-bottom: 20px;
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
  margin-bottom: 30px;
  font-size: 1rem;
}

.cards {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  min-width: 400px;
  text-align: center;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.card-label {
  color: #555;
  margin-bottom: 8px;
  font-size: 1rem;
}

.card-value {
  font-size: 1.4rem;
  font-weight: bold;
  color: #9b59d8;
}

.charts {
  display: flex;
  gap: 20px;
  justify-content: space-evenly;
  flex-wrap: nowrap; /* Mantém os três na mesma linha */
}

.chart-card {
  max-width: 600px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

canvas {
  width: 500PX !important;
  height: 250px !important;
  font-size: small;
}

.loading {
  text-align: center;
  color: #555;
  font-weight: bold;
  margin-top: 20px;
}
</style>
