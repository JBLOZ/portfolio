const express = require('express');
const path = require('path');
const axios = require('axios');
const app = express();
const PORT = 80;
// ¡El estudiante debe reemplazar esto con la IP privada de su instancia de back-end!
const BACKEND_API_URL = 'http://IP_PRIVADA_DEL_BACKEND:5000/predict';
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.post('/api/predict', async (req, res) => {
    try {
        const response = await axios.post(BACKEND_API_URL, req.body);
        res.json(response.data);
    } catch (error) {
        console.error('Error al conectar con el backend:', error.message);
        res.status(500).json({ error: 'No se pudo conectar con el servicio de análisis de sentimientos.' });
    }
});
app.listen(PORT, () => {
    console.log(`Servidor front-end escuchando en el puerto ${PORT}`);
});
