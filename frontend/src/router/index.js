import { createRouter, createWebHistory } from "vue-router";
import Operadoras from "../views/Operadoras.vue";
import DetalhesOperadora from "../views/DetalhesOperadora.vue";
import Estatisticas from "../views/Estatisticas.vue";

const routes = [
  { path: "/", component: Operadoras },
  { path: "/detalhes/:cnpj", component: DetalhesOperadora },
  { path: "/estatisticas", component: Estatisticas },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
