<template>
  <header class="navbar">
    <div class="logo">IntuitiveCare</div>

    <nav class="menu">
      <router-link to="/" exact>Operadoras</router-link>
      <router-link to="/estatisticas">Estatísticas</router-link>
    </nav>
  </header>
</template>

<script>
export default {
  name: "Navbar"
};
</script>

<style scoped>
.navbar {
  display: flex;
  
  justify-content: space-between; /* logo esquerda | menu direita */
  align-items: center;
  padding: 16px 60px;
}

.logo {
  font-size: 26px;       /* 🔥 aumenta a fonte */
  font-weight: 700;
  color: #ffffff;
}

.menu {
  display: flex;
  gap: 24px;             /* espaço entre links */
}

.menu a {
  color: #ffffff;
  text-decoration: none;
  font-size: 16px;
}

.menu a.router-link-active {
  font-weight: 600;
  border-bottom: 2px solid #38bdf8;
}
</style>
