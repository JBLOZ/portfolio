
### Introducción al Proyecto: Bot de Análisis de Sentimiento Bursátil

En un mundo financiero cada vez más dinámico y sobrecargado de información, tomar decisiones de inversión ágiles e informadas es un desafío constante. Los inversores, tanto novatos como experimentados, se enfrentan al reto de procesar grandes volúmenes de noticias, informes y opiniones para evaluar el sentimiento del mercado sobre un activo financiero. Este proceso no solo consume mucho tiempo, sino que también requiere un análisis complejo para extraer conclusiones prácticas.

Para abordar este problema, hemos desarrollado una solución innovadora: un **asistente conversacional inteligente a través de un bot de Telegram**, diseñado para realizar análisis de sentimiento de mercado para cualquier acción o ETF bajo demanda.

Nuestro proyecto nace de la necesidad de simplificar y automatizar el acceso a inteligencia de mercado. El objetivo principal es proporcionar a cualquier usuario una herramienta accesible desde su móvil que, con un simple comando, sea capaz de:
1.  **Recopilar las noticias más recientes** y relevantes sobre un activo financiero específico.
2.  **Utilizar un Modelo de Lenguaje Avanzado (LLM)** para analizar esta información y determinar el sentimiento general del mercado.
3.  **Generar una recomendación de inversión clara y concisa** a medio plazo, categorizada en acciones como compra fuerte, compra, mantener, vender o venta fuerte.

Para lograrlo, hemos diseñado y construido una arquitectura robusta que integra múltiples tecnologías. Utilizando **n8n** como plataforma central de automatización para orquestar el flujo de trabajo, **Docker** para crear el entorno de ejecución, y un túnel de **Cloudflare** para exponer nuestro servicio local a Internet de forma segura y asi poder permitir la entrada de mensajes mediante nuestro bot de telegram.

Este proyecto no solo resuelve un problema real, sino que también sirve como una demostración práctica de cómo la combinación de la automatización de flujos de trabajo, la inteligencia artificial conversacional y la infraestructura nos permite crear potentes aplicaciones con recursos limitados. A continuación, explicaremos en detalle cada uno de los pasos que hemos seguido para dar vida a este bot, desde la configuración del entorno hasta el diseño del flujo de inteligencia.

Claro, aquí tienes una propuesta para la introducción de tu seminario. He estructurado el texto para que sea claro, profesional y capte la atención, explicando el propósito y la relevancia del proyecto desde el primer momento.

***

### Configuración del Túnel y Scripts de Inicio

Para que nuestro bot de Telegram pueda recibir y procesar mensajes en tiempo real, es fundamental exponer el servidor local de n8n a Internet, ya que Telegram requiere una URL pública y accesible para configurar el webhook del trigger. Sin esta exposición, el trigger de Telegram no podría funcionar, ya que n8n opera por defecto en localhost:5678, un puerto interno no visible desde fuera. Elegimos Cloudflare Tunnel (cloudflared) por su simplicidad y gratuidad para entornos de desarrollo, aunque sus URLs generadas no son estáticas y cambian en cada ejecución, lo que impide hardcodearlas directamente en la configuración de n8n.

El desafío principal radica en esta variabilidad: si intentáramos definir una URL fija en el nodo de Telegram o en el docker-compose.yml, el webhook fallaría al reiniciar el servicio. Por ello, optamos por un enfoque dinámico basado en variables de entorno (.env), que permite inyectar la URL generada automáticamente en el contenedor de n8n sin intervención manual cada vez. Este método asegura que el trigger de Telegram apunte siempre a la URL correcta, usando variables como WEBHOOK_URL, N8N_HOST y TUNNEL_URL para configurar el protocolo HTTPS y el host externo.

#### Paso 1: Instalación y Preparación de Cloudflare Tunnel
Primero, instalamos cloudflared en nuestro sistema operativo (en este caso, Linux o WSL para compatibilidad con Docker). Este herramienta crea un túnel seguro desde nuestro puerto local (5678) hacia una URL temporal en el dominio trycloudflare.com, sin necesidad de cuenta ni configuración compleja. El comando base para iniciarlo es `cloudflared tunnel --url http://localhost:5678`, que genera una salida como "https://xxxx.trycloudflare.com" y la registra en un log para su captura posterior. Este túnel enruta el tráfico entrante de Telegram directamente a n8n, manteniendo la seguridad al no exponer puertos directamente en el firewall.

#### Paso 2: Creación del Script de Inicio (start-n8n.sh)
Para automatizar todo el proceso, creamos el script start-n8n.sh, que sigue un orden específico y secuencial para garantizar la integración sin errores. El script comienza deteniendo cualquier instancia previa de cloudflared o Docker para evitar conflictos: `pkill cloudflared 2>/dev/null` y `docker-compose down 2>/dev/null`. Luego, lanza cloudflared en segundo plano con redirección de salida a un archivo tunnel.log: `cloudflared tunnel --url http://localhost:5678 > tunnel.log 2>&1 &`, capturando el PID para control posterior.

A continuación, el script espera hasta 30 segundos para que se genere la URL, monitoreando el log con un bucle: `grep -oP 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' tunnel.log | head -1`.Una vez extraída la URL (por ejemplo, https://offline-argued-drops.trycloudflare.com), la valida y la almacena en una variable TUNNEL_URL. Si no se obtiene en el tiempo límite, el script falla con un error y mata el proceso de cloudflared. Este paso es crítico porque sin la URL dinámica, el webhook de Telegram no se configuraría correctamente en n8n.

#### Paso 3: Actualización de Variables de Entorno (.env)
Con la URL en mano, el script actualiza el archivo .env, que sirve como fuente de variables para docker-compose.yml. Genera o sobrescribe el .env con contenido como:
- WEBHOOK_URL=${TUNNEL_URL}
- N8N_HOST=${TUNNEL_URL} (adaptado para HTTPS)
- TUNNEL_URL=${TUNNEL_URL}

Esto inyecta la URL en el entorno de n8n, permitiendo que el nodo de Telegram use automáticamente WEBHOOK_URL como endpoint público. El script muestra el contenido del .env para verificación antes de proceder. De esta forma, evitamos editar manualmente el .env cada reinicio, haciendo el despliegue reproducible con un solo comando: `./start-n8n.sh`.

#### Paso 4: Lanzamiento del Contenedor de n8n
Finalmente, con el .env actualizado, el script ejecuta `docker-compose up -d`, iniciando el contenedor de n8n con las variables cargadas. El docker-compose.yml define el servicio n8n con puertos expuestos en 5678, volúmenes para persistencia de datos (/home/node/.n8n), y variables como N8N_PROTOCOL=https y N8N_EDITOR_BASE_URL=${TUNNEL_URL} para alinear la interfaz web y los webhooks. Una vez arriba, n8n configura internamente el webhook de Telegram apuntando a la URL del túnel, completando el ciclo de exposición. Para detener todo, usamos un script complementario stop-n8n.sh que hace down en Docker y mata cloudflared, limpiando logs opcionalmente.

Esta configuración no solo resuelve la exposición dinámica, sino que también mantiene el proyecto portable y escalable, ideal para demostraciones como esta. En la siguiente sección, detallaremos la creación del bot en Telegram y su integración en el workflow de n8n.


### Creación del Bot de Telegram e Integración del Trigger

Una vez configurado el túnel para exponer n8n a Internet, el siguiente paso esencial es crear el bot en Telegram y conectarlo al workflow mediante el nodo de trigger de Telegram, que actúa como punto de entrada para recibir mensajes del usuario. Este trigger se basa en la API de Telegram Bot, que requiere un token de autenticación para configurar un webhook que envíe actualizaciones de mensajes a nuestra URL pública (la generada por cloudflared). Sin esta integración, el bot no podría interactuar con el flujo de n8n, ya que Telegram solo notifica a endpoints accesibles externamente.[1]

#### Paso 1: Creación del Bot con BotFather
Para iniciar, abrimos Telegram y buscamos el usuario oficial @BotFather, que es la herramienta de Telegram para gestionar bots. Enviamos el comando `/newbot` seguido del nombre del bot (por ejemplo, "Stock Market Analytics Bot") y un username único terminando en "bot" (como @stock_market_analytics_bot), que debe ser público y accesible para todos los usuarios. BotFather responde confirmando la creación y proporcionando un **token de API** en formato `123456789:ABCDEF...`, que actúa como clave secreta para autenticar todas las peticiones del bot. Este token no debe compartirse públicamente, ya que otorga control total sobre el bot, incluyendo la capacidad de enviar y recibir mensajes.

#### Paso 2: Configuración del Nodo de Trigger en n8n
Con el token en mano, accedemos a la interfaz de n8n (vía la URL del túnel) y creamos un nuevo workflow, arrastrando el nodo **Telegram Trigger** al canvas. En las credenciales del nodo, seleccionamos "Create New" para la autenticación de Telegram, ingresando el token de API obtenido de BotFather y configurando el tipo como "Bot Token Authentication". El nodo también requiere la URL del webhook, que se resuelve automáticamente usando la variable de entorno WEBHOOK_URL del .env (injected vía docker-compose), apuntando a `https://[túnel].trycloudflare.com/webhook/[workflow-id]`, donde n8n maneja la ruta interna para actualizaciones. Al activar el workflow, n8n registra el webhook con la API de Telegram, confirmando que recibirá notificaciones push para cada mensaje enviado al bot. Esto asegura que el trigger se active solo para nuestro bot, filtrando interacciones irrelevantes por defecto.[1]

#### Paso 3: Estructura del Mensaje Entrante y Preparación para el Flujo
Cuando un usuario envía un mensaje al bot, como `/analysis sp500`, el trigger de Telegram recibe un JSON estructurado con la actualización completa del mensaje, que incluye metadatos del usuario y el chat para contextualizar la interacción. La estructura típica es un array de objetos con campos como `update_id` (identificador único de la actualización), `message` (detalles del mensaje), que contiene `message_id`, `from` (información del emisor con `id` numérico), `chat` (detalles del chat con el mismo `id`), `date` (timestamp), `text` (contenido del mensaje, e.g., "/analysis sp500") y `entities` (anotaciones como comandos de bot). Por ejemplo, un mensaje de prueba genera algo como:

```
[
  {
    "update_id": 177484711,
    "message": {
      "message_id": 20,
      "from": {
        "id": 1065676350,
        "is_bot": false,
        "first_name": "Jordi",
        "last_name": "Blasco Lozano",
        "username": "jbloz",
        "language_code": "es"
      },
      "chat": {
        "id": 1065676350,
        "first_name": "Jordi",
        "last_name": "Blasco Lozano",
        "username": "jbloz",
        "type": "private"
      },
      "date": 1761410615,
      "text": "/analysis sp500",
      "entities": [
        {
          "offset": 0,
          "length": 9,
          "type": "bot_command"
        }
      ]
    }
  }
]
```

Este formato detallado es útil para tracking, pero para nuestro flujo de análisis de sentimiento, necesitamos simplificarlo extrayendo solo los elementos esenciales: el texto después del comando (e.g., "sp500") y el ID del usuario (e.g., 1065676350) para respuestas posteriores. Por lo tanto, transformamos el JSON entrante en una estructura minimalista como:

```
[
  {
    "text": "sp500",
    "id": 1065676350
  }
]
```

Esta reformateación se logra en los nodos subsiguientes (filtro y código JavaScript), eliminando ruido como nombres, timestamps y entidades, para pasar datos limpios al resto del workflow sin sobrecargar el procesamiento. De esta manera, el trigger inicializa el flujo de forma eficiente, preparando el terreno para la validación y extracción de comandos específicos como `/analysis`.

En la próxima sección, detallaremos cómo filtramos mensajes irrelevantes y refinamos el texto extraído mediante nodos de código.

### Transformación y filtrado de los datos de entrada: Nodos Filter y JavaScript en n8n

Una vez que el trigger de Telegram recibe los mensajes enviados al bot, el siguiente paso en el workflow de n8n es limpiar y transformar los datos para quedarnos solo con la información relevante para nuestro análisis bursátil. El objetivo aquí es filtrar solo los mensajes que contengan el comando `/analysis` y extraer el texto posterior al comando (el ticker o nombre del activo) junto al identificador de usuario para personalizar las respuestas en el resto del flujo.[1][3]

#### Paso 1: Nodo de Filter

El nodo **Filter** funciona como una puerta de acceso, permitiendo únicamente los mensajes que cumplen una condición clave: que el mensaje incluya la palabra `/analysis`. Así, si un usuario escribe cualquier otro texto o comando, el flujo lo descartará automáticamente y no avanzará a las siguientes etapas. Esta lógica reduce ruido y asegura que solo procesamos peticiones válidas y estructuradas para el análisis del sentimiento de mercado.[2][1]

- **Configuración**: 
  - Campo a filtrar: `message.text` (dentro del JSON recibido).
  - Condición: contiene `/analysis`.
  - Acción: si pasa el filtro, el mensaje sigue el flujo; si no, se descarta.

#### Paso 2: Nodo Code (JavaScript)

El nodo **Code** o **Code in JavaScript** es donde transformamos el mensaje filtrado en un formato sencillo y funcional para el resto del workflow. El bloque de código que has incluido cumple tres funciones principales:

- Toma el texto completo del mensaje (`fullText`) y el identificador del usuario (`ID`).
- Localiza el comando `/analysis` y extrae únicamente el texto que viene detrás (lo que el usuario quiere analizar: un ticker, índice, etc.).
- Devuelve un objeto JSON minimalista con el formato exactamente necesario para la API siguiente: el `text` limpio y el `id` para enviar la respuesta al usuario correcto.

```javascript
const fullText = $input.item.json.message.text;
const ID = $input.item.json.message.from.id;
const command = "/analysis ";

// Extrae todo lo que viene después de /analysis
const textAfterCommand = fullText.includes(command) 
  ? fullText.substring(fullText.indexOf(command) + command.length).trim()
  : fullText;

return {
  json: {
    text: textAfterCommand,
    id: ID
  }
};
```

Gracias a esto, transformamos un mensaje de entrada complejo, como el que hemos visto en el paso anterior en una salida simple y limpia como esta:

```
[
  {
    "text": "sp500",
    "id": 1065676350
  }
]
```

Esto prepara el mensaje para ser enviado a la API de análisis de sentimiento o cualquier otro módulo de procesamiento posterior, facilitando al máximo la integración y manteniendo limpio el flujo de trabajo en n8n.


### Paso siguiente: HTTP Request para buscar noticias con Perplexity API

Una vez que hemos procesado el mensaje del usuario para obtener únicamente el texto relevante (el ticker o nombre del activo financiero), el siguiente paso del workflow consiste en consultar la API de Perplexity para recopilar las noticias más recientes sobre ese activo. Esta búsqueda es fundamental para que el LLM realice el análisis de sentimiento con información actualizada y relevante.

#### Perplexity, subscripción y API
Perplexity ofrece varias maneras de acceder a su API Pro, incluyendo un periodo de prueba de 12 meses si asocias una cuenta de PayPal, así como promociones puntuales para ciertas cuentas o estudiantes. En nuestro caso, disponemos de una suscripción Pro, que nos da acceso prioritario tanto a modelos avanzados como a la propia API. Esta suscripción incluye **5 € de crédito API cada mes**, suficiente para mantener proyectos ligeros y pruebas recurrentes.

#### Acceso a la API de búsqueda
Con la suscripción Pro, tenemos acceso directo a la API, incluida la función más potente: la **API de búsqueda avanzada**. La documentación oficial de Perplexity proporciona un ejemplo de integración rápida mediante cURL (que podemos copiar y pegar al módulo de HTTP Request en n8n), autenticando cada llamada con nuestra clave personal. Allí mismo se detallan parámetros de uso como el límite de resultados o el máximo de tokens por noticia.

#### Ejemplo práctico de la integración en n8n
Creamos un módulo HTTP Request justo después del bloque de JavaScript, usando estos ajustes:
- **URL:** `https://api.perplexity.ai/search`
- **Método:** POST
- **Autenticación:** Bearer Token (clave API de Perplexity)
- **Cuerpo (JSON):**
  ```json
  {
    "query": [
        "Last news about {{ $json.text }}",
        "{{ $json.text }} financial asset forecasts",
        "{{ $json.text }} financial asset last results"
    ],
    "max_results": 8
  }
  ```
Aquí, `{{ $json.text }}` toma el ticker del paso anterior para personalizar la búsqueda. Para enriquecer los resultados, no nos limitamos a una sola consulta, sino que realizamos tres búsquedas simultáneas sobre el mismo activo, solicitando noticias recientes, previsiones y los últimos resultados financieros. Esto proporciona un contexto mucho más rico para el análisis posterior.



---
### Formateo de Noticias y Preparación para el Análisis (Code in JavaScript4)

Tras la llamada exitosa a la API de Perplexity (`HTTP Request1`), el workflow recibe un objeto JSON complejo que contiene una lista de noticias. Esta estructura, aunque rica en datos (con URLs, snippets, metadatos, etc.), no es un formato óptimo para ser analizada directamente por un Modelo de Lenguaje (LLM). Para maximizar la precisión del análisis y minimizar el consumo de tokens, es crucial "limpiar" y "condensar" esta información.

Esta tarea la realiza el nodo **Code in JavaScript4**. Su función es iterar sobre el array de resultados de la búsqueda y concatenar la información esencial de cada noticia (como el título y el resumen o snippet) en un único bloque de texto plano. Este bloque de texto se formatea de manera legible, separando cada noticia para que el LLM pueda distinguirlas.

Además, este nodo inicializa un contador de reintentos (`retry_count: 0`), que será clave para la lógica de corrección que veremos más adelante.

El resultado es un objeto JSON que contiene el `text` (nombre del activo), las `noticias` (el texto plano con toda la información) y el `retry_count`, sirviendo como la única "fuente de verdad" para los siguientes pasos de análisis.

---
### Arquitectura de "Actor-Crítico": El Proceso de Análisis y Revisión

Para asegurar una alta fiabilidad en la respuesta y evitar las "alucinaciones" (respuestas incorrectas o inventadas) de la IA, implementamos una arquitectura avanzada de dos agentes conocida como **Actor-Crítico**. En lugar de confiar en un solo agente, uno genera el análisis (el "Actor") y un segundo agente, más estricto, lo revisa (el "Crítico").

#### Paso 1: El Actor - `AI Agent2` (Analista)

El primer agente, **`AI Agent2`**, actúa como el "Analista". Recibe el contexto de noticias formateado del nodo anterior. Su *prompt* (instrucción) le ordena realizar el análisis completo y responder **únicamente** con un formato de texto estricto que hemos definido:

```
Compra: [X]%
Mantener: [Y]%
Vender: [Z]%
Expectativa: [Alcista o Bajista]
Resumen: [Un resumen de un párrafo de las noticias...]
```
Este formato simple basado en texto es fácil de generar para el modelo, pero aún puede contener errores. La salida de este nodo es un único *string* de texto.

#### Paso 2: El Crítico - `AI Agent3` (Revisor)

Aquí es donde entra el control de calidad. El segundo agente, **`AI Agent3`**, actúa como el "Revisor". Este nodo recibe dos entradas cruciales:
1.  El **contexto de noticias original** (del nodo `Code in JavaScript4`).
2.  El **análisis en texto** generado por el primer agente (la salida de `AI Agent2`).

La tarea del Revisor no es generar un análisis, sino **juzgar** el análisis del Actor. Su *prompt* le instruye a comparar el resumen y los porcentajes con las noticias originales y determinar si el análisis está 100% justificado por ellas.

Para que su decisión sea utilizable por el workflow, forzamos su salida a un simple "True" o "False".

---
### Flujo Condicional: El Bucle de Corrección y Fusión

La salida del Revisor nos permite crear un flujo condicional para simular un "bucle de re-intento".

#### Paso 1: El Nodo `If1`

Este nodo lee la salida del `AI Agent3` (Revisor). Su condición es si la salida contiene "True" y si el análisis del `AI Agent2` contiene las palabras clave esperadas ("Compra:", "Mantener:", etc.). Esto crea dos ramas:
* **Rama "True" (Éxito):** El análisis es bueno y puede continuar.
* **Rama "False" (Error):** El análisis es malo o incompleto y necesita ser rehecho.

#### Paso 2: La Rama "False" (Re-intento del Actor)

Esta rama es la clave de nuestra lógica de "loop". Cuando el análisis es `false`, el flujo se dirige al nodo `Code Increment Retry`, que aumenta en uno el contador de reintentos. Después, el nodo `If Max Retry` comprueba si se ha alcanzado el límite de 3 reintentos. Si no se ha alcanzado, el flujo vuelve al `AI Agent2` para que genere un nuevo análisis. Si se alcanza el límite, el flujo termina en un error.

#### Paso 3: La Fusión de Ramas

La rama "True" del nodo `If1` se conecta directamente al nodo final de formateo, `Code in JavaScript5`.

---
### Formateo Final y Respuesta al Usuario

#### `Code in JavaScript5` (Formateador Avanzado)

Este es el nodo de código que prepara la respuesta final. Su trabajo es tomar el análisis *final y aprobado* y convertirlo en el mensaje que verá el usuario. Su lógica interna hace lo siguiente:

1.  **Extracción con Regex:** Toma el `aiResponse` (el texto del análisis correcto del `AI Agent2`) y utiliza **Expresiones Regulares (`.match()`)** para extraer los valores de cada línea (ej: `Compra: (\d+)%`).
2.  **Formateo HTML:** Finalmente, construye el mensaje de respuesta usando **etiquetas HTML** (como `<b>` para negrita) para darle estilo, incluyendo emojis (`📈` o `📉`) según la expectativa.

#### `Send a text message1` (Envío por Telegram)

Este es el último nodo. Recibe el `responseText` (el texto HTML) del nodo anterior y lo envía al usuario. La configuración clave aquí es:
* **`Chat ID`:** Se obtiene dinámicamente del *primer* nodo del flujo (`Telegram Trigger`), asegurando que la respuesta siempre vuelva al usuario que hizo la petición.
* **`Parse Mode`:** Se establece en **`HTML`** para que Telegram interprete correctamente las etiquetas `<b>` y `•` que hemos definido.

Este ciclo completo asegura que el usuario reciba una respuesta no solo rápida, sino también verificada, fiable y formateada profesionalmente.