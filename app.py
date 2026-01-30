import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    layout="wide", 
    page_title="Estrategia de Producto y Marca",
    page_icon="🎯",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .concept-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .quiz-option {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .quiz-option:hover {
        background-color: #d0e8f2;
        transform: translateX(5px);
    }
    .correct-answer {
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .incorrect-answer {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
    .progress-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        background-color: #ffc107;
        color: white;
        font-weight: bold;
        margin: 0.5rem;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE SESSION STATE ---
if 'progreso' not in st.session_state:
    st.session_state.progreso = {
        'conceptos_vistos': set(),
        'quizzes_completados': set(),
        'casos_resueltos': set(),
        'puntos_totales': 0,
        'nivel': 'Principiante'
    }

if 'diagnostico_completado' not in st.session_state:
    st.session_state.diagnostico_completado = False

if 'respuestas_diagnostico' not in st.session_state:
    st.session_state.respuestas_diagnostico = {}

if 'marca_creada' not in st.session_state:
    st.session_state.marca_creada = {}

if 'quiz_actual' not in st.session_state:
    st.session_state.quiz_actual = {
        'pregunta_idx': 0,
        'respuestas': [],
        'puntuacion': 0
    }

# --- DATOS DE CONCEPTOS POR CAPÍTULO ---
CONCEPTOS_CLAVE = {
    "Cap 1: Marketing Estratégico": {
        "Marketing 6.0": {
            "definicion": "Evolución del marketing que integra tecnología avanzada (IA, big data) con humanismo, enfocándose en la creación de valor humano, bienestar social y sostenibilidad.",
            "ejemplo": "Una marca que usa IA para personalizar experiencias, pero siempre priorizando el propósito social y la transparencia.",
            "pregunta": "¿Cuál es el elemento diferenciador clave del Marketing 6.0?",
            "opciones": [
                "Solo el uso de tecnología avanzada",
                "La convergencia de tecnología y humanismo",
                "El enfoque exclusivo en ventas",
                "La eliminación de la ética empresarial"
            ],
            "respuesta_correcta": 1
        },
        "Producto y Marca": {
            "definicion": "El producto materializa la propuesta de valor; la marca funciona como sistema de significados que identifica, diferencia y dota de sentido dicha propuesta.",
            "ejemplo": "iPhone como producto (tecnología) + Apple como marca (innovación, diseño, estatus).",
            "pregunta": "¿Cuál es la relación correcta entre producto y marca?",
            "opciones": [
                "Son conceptos idénticos e intercambiables",
                "El producto es tangible, la marca es el sistema de significados",
                "Solo el producto importa para la competitividad",
                "La marca es solo el logo de la empresa"
            ],
            "respuesta_correcta": 1
        }
    },
    
    "Cap 2: Creación de Valor": {
        "Orientación al Mercado": {
            "definicion": "Capacidad de la organización para identificar, comprender y satisfacer las necesidades del consumidor mejor que la competencia.",
            "ejemplo": "Netflix estudiando hábitos de consumo para crear contenido original personalizado.",
            "pregunta": "La orientación al mercado implica principalmente:",
            "opciones": [
                "Producir lo que la empresa sabe hacer",
                "Identificar y satisfacer necesidades del consumidor",
                "Reducir costos de producción",
                "Copiar a la competencia"
            ],
            "respuesta_correcta": 1
        },
        "Propuesta de Valor": {
            "definicion": "Conjunto de beneficios que una empresa promete entregar al consumidor para satisfacer sus necesidades de manera diferenciada.",
            "ejemplo": "Volvo: seguridad como propuesta central de valor.",
            "pregunta": "Una propuesta de valor efectiva debe:",
            "opciones": [
                "Ser genérica para atraer a todos",
                "Diferenciarse y ser relevante para el segmento objetivo",
                "Enfocarse solo en precio bajo",
                "Cambiar constantemente"
            ],
            "respuesta_correcta": 1
        }
    },
    
    "Cap 3: El Producto": {
        "Niveles del Producto": {
            "definicion": "Producto básico (beneficio esencial), producto real (atributos tangibles/intangibles), producto aumentado (servicios adicionales y experiencias).",
            "ejemplo": "Hotel: básico=alojamiento, real=habitación+diseño+marca, aumentado=spa+wifi+concierge.",
            "pregunta": "El 'producto aumentado' se refiere a:",
            "opciones": [
                "El beneficio esencial que busca el consumidor",
                "Los atributos físicos del producto",
                "Servicios adicionales y experiencias complementarias",
                "El precio del producto"
            ],
            "respuesta_correcta": 2
        },
        "Clasificación de Productos": {
            "definicion": "Conveniencia (compra frecuente/rápida), Comparación (evaluación previa), Especialidad (características únicas), No buscados (desconocidos).",
            "ejemplo": "Conveniencia=chicle, Comparación=TV, Especialidad=Rolex, No buscado=seguro funerario.",
            "pregunta": "Un producto de especialidad se caracteriza por:",
            "opciones": [
                "Compra rápida sin comparación",
                "Evaluación de múltiples alternativas",
                "Características únicas que motivan esfuerzo especial de compra",
                "Ser desconocido para el consumidor"
            ],
            "respuesta_correcta": 2
        }
    },
    
    "Cap 4: Ciclo de Vida": {
        "Etapas del CVP": {
            "definicion": "Introducción (lanzamiento), Crecimiento (aceptación), Madurez (saturación), Declive (disminución).",
            "ejemplo": "Introducción=auto eléctrico en 2010, Crecimiento=Tesla 2015-2020, Madurez=smartphone 2023.",
            "pregunta": "¿En qué etapa del CVP la competencia es más intensa?",
            "opciones": [
                "Introducción",
                "Crecimiento",
                "Madurez",
                "Declive"
            ],
            "respuesta_correcta": 2
        },
        "Estrategias por Etapa": {
            "definicion": "Cada etapa requiere ajustes en producto, precio, distribución y comunicación según condiciones del mercado.",
            "ejemplo": "Introducción: comunicación informativa; Madurez: comunicación persuasiva y promociones.",
            "pregunta": "En la etapa de madurez, la estrategia típica es:",
            "opciones": [
                "Informar sobre la existencia del producto",
                "Retirarse del mercado",
                "Defender participación y buscar diferenciación",
                "Aumentar drásticamente los precios"
            ],
            "respuesta_correcta": 2
        }
    },
    
    "Cap 7-8: Marca": {
        "Identidad vs Imagen": {
            "definicion": "Identidad: cómo la empresa define la marca (interno). Imagen: cómo el consumidor percibe la marca (externo). Reputación: percepción acumulada en el tiempo.",
            "ejemplo": "Nike define identidad como 'inspiración atlética' → consumidores pueden percibirla como 'motivación' o 'élite deportiva'.",
            "pregunta": "La diferencia clave entre identidad e imagen de marca es:",
            "opciones": [
                "No hay diferencia, son lo mismo",
                "Identidad es interna (empresa), imagen es externa (consumidor)",
                "Identidad es visual, imagen es conceptual",
                "Solo la imagen importa"
            ],
            "respuesta_correcta": 1
        },
        "Equidad de Marca": {
            "definicion": "Valor adicional que la marca aporta al producto más allá de características funcionales (brand equity).",
            "ejemplo": "Dos bolsos idénticos: uno sin marca $50, otro con logo Louis Vuitton $1,500 (equidad de marca).",
            "pregunta": "La equidad de marca se refiere a:",
            "opciones": [
                "El costo de producción de la marca",
                "El valor adicional que la marca aporta al producto",
                "El número de productos en el portafolio",
                "La edad de la marca en el mercado"
            ],
            "respuesta_correcta": 1
        },
        "Estrategias de Marca": {
            "definicion": "Individual (marca por producto), Corporativa (un nombre para todo), Extensión (marca existente a nuevo producto), Co-branding (alianza).",
            "ejemplo": "Individual=P&G (Pampers, Ariel, Gillette), Corporativa=Samsung, Extensión=Dove jabón→shampoo.",
            "pregunta": "La extensión de marca consiste en:",
            "opciones": [
                "Crear una nueva marca desde cero",
                "Aplicar marca existente a nuevos productos/categorías",
                "Eliminar productos del portafolio",
                "Cambiar el nombre de la marca"
            ],
            "respuesta_correcta": 1
        }
    }
}

# ... (continúa desde la parte anterior)

# --- BANCO DE PREGUNTAS PARA QUIZ ADAPTATIVO ---
BANCO_PREGUNTAS = {
    "basico": [
        {
            "pregunta": "¿Qué es el Marketing 6.0?",
            "opciones": [
                "Marketing tradicional en redes sociales",
                "Convergencia de tecnología avanzada y humanismo",
                "Marketing enfocado solo en ventas online",
                "Eliminación del marketing físico"
            ],
            "correcta": 1,
            "explicacion": "Marketing 6.0 integra IA, big data y automatización al servicio de la creación de valor humano, bienestar social y sostenibilidad.",
            "tema": "Fundamentos"
        },
        {
            "pregunta": "El producto básico representa:",
            "opciones": [
                "Los atributos físicos del producto",
                "El beneficio esencial que busca el consumidor",
                "Los servicios adicionales",
                "El precio más bajo del mercado"
            ],
            "correcta": 1,
            "explicacion": "El producto básico es el beneficio fundamental que satisface la necesidad del consumidor (ej: un hotel ofrece alojamiento como beneficio básico).",
            "tema": "Producto"
        },
        {
            "pregunta": "¿Cuál NO es una etapa del ciclo de vida del producto?",
            "opciones": [
                "Introducción",
                "Expansión internacional",
                "Madurez",
                "Declive"
            ],
            "correcta": 1,
            "explicacion": "Las 4 etapas del CVP son: Introducción, Crecimiento, Madurez y Declive. La expansión internacional es una estrategia, no una etapa.",
            "tema": "Ciclo de Vida"
        },
        {
            "pregunta": "La marca funciona como:",
            "opciones": [
                "Solo un logo visual",
                "Un sistema de significados que identifica y diferencia",
                "El precio del producto",
                "La publicidad de la empresa"
            ],
            "correcta": 1,
            "explicacion": "La marca es un sistema de significados que permite identificar, diferenciar y dotar de sentido a la propuesta de valor.",
            "tema": "Marca"
        },
        {
            "pregunta": "La orientación al mercado implica:",
            "opciones": [
                "Producir lo que la empresa quiere",
                "Identificar y satisfacer necesidades del consumidor",
                "Reducir costos sin importar la calidad",
                "Copiar todos los productos de la competencia"
            ],
            "correcta": 1,
            "explicacion": "La orientación al mercado significa comprender y satisfacer las necesidades del consumidor mejor que la competencia.",
            "tema": "Creación de Valor"
        }
    ],
    
    "intermedio": [
        {
            "pregunta": "En la etapa de madurez del CVP, ¿cuál estrategia es más apropiada?",
            "opciones": [
                "Retirarse inmediatamente del mercado",
                "Modificar el mercado, producto o marketing mix",
                "Aumentar precios drásticamente",
                "Eliminar toda la comunicación"
            ],
            "correcta": 1,
            "explicacion": "En madurez se busca prolongar la vida del producto mediante modificaciones del mercado (nuevos segmentos), producto (mejoras) o marketing mix.",
            "tema": "Ciclo de Vida"
        },
        {
            "pregunta": "¿Qué diferencia a la identidad de marca de la imagen de marca?",
            "opciones": [
                "Son conceptos idénticos",
                "Identidad es cómo la empresa define la marca; imagen es la percepción del consumidor",
                "Identidad es el logo; imagen es el slogan",
                "No hay diferencia real entre ambas"
            ],
            "correcta": 1,
            "explicacion": "Identidad es la construcción interna (empresa), imagen es la percepción externa (consumidor). La identidad no está completamente bajo control de la empresa.",
            "tema": "Marca"
        },
        {
            "pregunta": "La extensión de marca implica:",
            "opciones": [
                "Crear una marca completamente nueva",
                "Aplicar una marca existente a nuevos productos o categorías",
                "Cambiar el nombre de la marca actual",
                "Fusionarse con otra empresa"
            ],
            "correcta": 1,
            "explicacion": "La extensión de marca aprovecha la equidad de marca existente para lanzar nuevos productos, reduciendo costos y facilitando aceptación.",
            "tema": "Estrategias de Marca"
        },
        {
            "pregunta": "Un producto de especialidad se caracteriza por:",
            "opciones": [
                "Compra frecuente sin pensar",
                "Comparación exhaustiva de alternativas",
                "Características únicas que justifican esfuerzo especial de compra",
                "Ser completamente desconocido"
            ],
            "correcta": 2,
            "explicacion": "Los productos de especialidad (ej: Rolex, Ferrari) tienen atributos únicos o fuerte identificación de marca que motivan al consumidor a hacer esfuerzo para adquirirlos.",
            "tema": "Producto"
        },
        {
            "pregunta": "El co-branding consiste en:",
            "opciones": [
                "Eliminar una marca del portafolio",
                "La asociación de dos o más marcas para un producto/servicio",
                "Reducir el precio de la marca",
                "Cambiar el logo de la marca"
            ],
            "correcta": 1,
            "explicacion": "Co-branding es la alianza estratégica entre marcas para combinar fortalezas y crear propuestas diferenciadas (ej: Nike + Apple).",
            "tema": "Estrategias de Marca"
        }
    ],
    
    "avanzado": [
        {
            "pregunta": "¿Cuál es el principal riesgo del greenwashing en productos verdes?",
            "opciones": [
                "Aumentar las ventas temporalmente",
                "Pérdida de credibilidad y daño reputacional grave",
                "Reducir los costos de producción",
                "Mejorar la imagen de marca"
            ],
            "correcta": 1,
            "explicacion": "El greenwashing (comunicar sostenibilidad falsa) genera desconfianza, afecta la reputación y puede tener consecuencias legales en el contexto del Marketing 6.0.",
            "tema": "Sostenibilidad"
        },
        {
            "pregunta": "Según el caso Frisby, ¿cuál es la lección estratégica clave sobre marcas?",
            "opciones": [
                "No es necesario registrar marcas internacionalmente",
                "El registro marcario debe acompañarse de uso real y vigilancia",
                "Las marcas no tienen valor legal",
                "Solo importa el registro en el país de origen"
            ],
            "correcta": 1,
            "explicacion": "El caso Frisby enseña que la protección marcaria requiere planificación internacional, uso real y vigilancia constante, incluso en territorios donde aún no se opera.",
            "tema": "Aspectos Legales"
        },
        {
            "pregunta": "En el contexto del Marketing 6.0, ¿qué implica la 'economía de la experiencia'?",
            "opciones": [
                "Reducir precios al mínimo",
                "Competir por experiencias memorables, no solo atributos funcionales",
                "Eliminar el servicio al cliente",
                "Enfocarse solo en productos tangibles"
            ],
            "correcta": 1,
            "explicacion": "Pine y Gilmore introducen la economía de la experiencia: las empresas compiten creando experiencias inmersivas que integran beneficios funcionales, emocionales y simbólicos.",
            "tema": "Fundamentos Avanzados"
        },
        {
            "pregunta": "¿Qué representa la equidad de marca según Aaker?",
            "opciones": [
                "Solo el reconocimiento visual del logo",
                "Conjunto de activos y pasivos vinculados a la marca que agregan o restan valor",
                "El precio de venta de los productos",
                "El número de empleados de la empresa"
            ],
            "correcta": 1,
            "explicacion": "Aaker define brand equity como activos/pasivos vinculados al nombre y símbolo de la marca que impactan el valor percibido por consumidores y empresa.",
            "tema": "Marca Avanzado"
        },
        {
            "pregunta": "En una declaración de posicionamiento, ¿qué elementos son esenciales?",
            "opciones": [
                "Solo el nombre de la marca",
                "Público objetivo, categoría, diferenciación y beneficio",
                "Únicamente el precio del producto",
                "Solo la descripción física del producto"
            ],
            "correcta": 1,
            "explicacion": "Una declaración de posicionamiento efectiva debe incluir: para quién (público), qué es (categoría), por qué es diferente (diferenciación) y qué entrega (beneficio).",
            "tema": "Posicionamiento"
        }
    ]
}

# --- CASOS DE DECISIÓN ESTRATÉGICA ---
CASOS_ESTRATEGICOS = {
    "caso_frisby": {
        "titulo": "Caso Frisby: El Conflicto Marcario",
        "contexto": """
        Frisby, cadena colombiana de pollo, expandió su operación sin registrar su marca en todos 
        los países de interés. Años después, al intentar ingresar a Panamá, descubrió que un tercero 
        había registrado "Frisby" y operaba un negocio similar.
        
        **Situación:** Como gerente de marca de Frisby, ¿qué estrategia recomendarías?
        """,
        "opciones": [
            {
                "texto": "Cambiar el nombre de la marca en Panamá",
                "consecuencia": "Se pierde la equidad de marca construida. Los consumidores no reconocen la nueva marca. Inversión en rebranding.",
                "correcta": False,
                "aprendizaje": "Cambiar el nombre diluye la equidad de marca y genera confusión. No es la solución estratégica óptima."
            },
            {
                "texto": "Negociar la compra de los derechos marcarios",
                "consecuencia": "Costo elevado pero se recupera la marca. Permite continuidad de identidad y equidad. Estrategia viable a largo plazo.",
                "correcta": True,
                "aprendizaje": "La negociación permite recuperar el activo marcario y mantener la coherencia de la estrategia de marca internacional."
            },
            {
                "texto": "Iniciar disputa legal sin analizar el contexto",
                "consecuencia": "Proceso largo, costoso y sin garantía de éxito si el registro del tercero es legítimo. Desgaste de recursos.",
                "correcta": False,
                "aprendizaje": "La vía legal sin análisis previo es riesgosa. Debe evaluarse la legitimidad del registro y viabilidad jurídica."
            },
            {
                "texto": "Ignorar el problema y operar con otra identidad",
                "consecuencia": "Se pierden años de construcción de marca. Fragmentación de la identidad corporativa. Confusión en mercados regionales.",
                "correcta": False,
                "aprendizaje": "Ignorar la protección marcaria genera problemas estratégicos graves a futuro. La prevención es clave."
            }
        ],
        "leccion_final": """
        **Lecciones clave del caso Frisby:**
        1. El registro marcario debe planificarse internacionalmente desde el inicio
        2. La protección debe acompañarse de uso real en los mercados
        3. La vigilancia marcaria es esencial para detectar conflictos temprano
        4. La marca es un activo vulnerable sin gestión legal-estratégica integrada
        """
    },
    
    "caso_producto_verde": {
        "titulo": "Dilema: Producto Verde vs Greenwashing",
        "contexto": """
        Tu empresa de cosméticos quiere lanzar una línea "eco-friendly". El equipo de marketing 
        propone comunicar "100% natural" aunque solo el 60% de ingredientes lo sean. 
        Argumentan que la competencia hace lo mismo y genera más ventas.
        
        **Situación:** Como gerente de producto, ¿qué decides?
        """,
        "opciones": [
            {
                "texto": "Aprobar la campaña '100% natural' para competir",
                "consecuencia": "Ventas iniciales altas. A mediano plazo: denuncia de consumidores, multas, pérdida de confianza, daño reputacional irreparable.",
                "correcta": False,
                "aprendizaje": "El greenwashing genera ganancias cortoplacistas pero destruye la reputación y credibilidad de marca a largo plazo."
            },
            {
                "texto": "Comunicar honestamente '60% ingredientes naturales'",
                "consecuencia": "Ventas iniciales moderadas, pero construcción de confianza. Diferenciación por transparencia. Lealtad a largo plazo.",
                "correcta": True,
                "aprendizaje": "La transparencia es un pilar del Marketing 6.0. Los consumidores valoran la honestidad y castigan el engaño."
            },
            {
                "texto": "Lanzar sin ninguna comunicación ambiental",
                "consecuencia": "Se pierde la oportunidad de diferenciación. El producto no aprovecha el beneficio real del 60% natural. Posicionamiento débil.",
                "correcta": False,
                "aprendizaje": "No comunicar los atributos reales es desperdiciar una ventaja competitiva legítima."
            },
            {
                "texto": "Mejorar la fórmula al 100% natural antes de lanzar",
                "consecuencia": "Retraso en el lanzamiento y mayores costos, pero propuesta auténtica. Comunicación coherente y sin riesgos legales.",
                "correcta": True,
                "aprendizaje": "Alinear el producto con la comunicación es la estrategia más sostenible. La autenticidad genera valor a largo plazo."
            }
        ],
        "leccion_final": """
        **Lecciones sobre sostenibilidad y ética:**
        1. El Marketing 6.0 exige coherencia entre discurso y acción
        2. Los consumidores contemporáneos valoran la transparencia
        3. El greenwashing destruye la credibilidad de marca
        4. La sostenibilidad es una exigencia del mercado, no una opción
        """
    },
    
    "caso_extension_marca": {
        "titulo": "Extensión de Marca: ¿Oportunidad o Riesgo?",
        "contexto": """
        Tu empresa de ropa deportiva de alta gama (posicionada en calidad premium) quiere lanzar 
        una línea de productos económicos para captar el mercado masivo. El equipo comercial 
        asegura que duplicará las ventas.
        
        **Situación:** ¿Qué estrategia de marca recomiendas?
        """,
        "opciones": [
            {
                "texto": "Usar la misma marca premium para la línea económica",
                "consecuencia": "Confusión en el posicionamiento. Dilución de la percepción de calidad. Clientes premium abandonan la marca.",
                "correcta": False,
                "aprendizaje": "Extender una marca premium a segmentos económicos puede diluir la equidad de marca y generar confusión."
            },
            {
                "texto": "Crear una marca individual diferente para la línea económica",
                "consecuencia": "Protección de la marca premium. Segmentación clara. Mayores costos de marketing, pero sin riesgo de dilución.",
                "correcta": True,
                "aprendizaje": "Las marcas individuales permiten posicionamientos diferenciados y reducen el riesgo para la marca principal."
            },
            {
                "texto": "Usar una sub-marca (ej: 'Marca Sport Lite')",
                "consecuencia": "Aprovecha reconocimiento de marca matriz pero diferencia. Estrategia intermedia con menor riesgo de dilución.",
                "correcta": True,
                "aprendizaje": "Las sub-marcas permiten extensiones manteniendo conexión con la marca principal pero con diferenciación."
            },
            {
                "texto": "Cancelar el proyecto de línea económica",
                "consecuencia": "Se mantiene la integridad de marca premium, pero se pierde oportunidad de crecimiento en otro segmento.",
                "correcta": False,
                "aprendizaje": "No siempre es necesario cancelar oportunidades; existen estrategias de marca que permiten diversificación sin dilución."
            }
        ],
        "leccion_final": """
        **Lecciones sobre extensión de marca:**
        1. Las extensiones deben ser coherentes con la identidad de marca
        2. La dilución de marca es un riesgo real en extensiones mal gestionadas
        3. Existen alternativas estratégicas: marcas individuales, sub-marcas, etc.
        4. La decisión debe basarse en equidad de marca y posicionamiento actual
        """
    }
}

# --- FUNCIONES AUXILIARES ---

def calcular_nivel_estudiante(progreso):
    """Calcula el nivel del estudiante basado en su progreso"""
    puntos = progreso['puntos_totales']
    if puntos < 100:
        return "🌱 Principiante", "#95a5a6"
    elif puntos < 300:
        return "📚 Aprendiz", "#3498db"
    elif puntos < 600:
        return "🎯 Competente", "#9b59b6"
    elif puntos < 1000:
        return "⭐ Avanzado", "#e67e22"
    else:
        return "🏆 Experto", "#f39c12"

def actualizar_puntos(puntos):
    """Actualiza los puntos del estudiante"""
    st.session_state.progreso['puntos_totales'] += puntos
    nivel, color = calcular_nivel_estudiante(st.session_state.progreso)
    st.session_state.progreso['nivel'] = nivel

# ... (continúa desde la parte anterior)

def mostrar_progreso_global():
    """Muestra el progreso general del estudiante"""
    progreso = st.session_state.progreso
    nivel, color = calcular_nivel_estudiante(progreso)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Puntos Totales", progreso['puntos_totales'])
    with col2:
        st.metric("📖 Conceptos Vistos", len(progreso['conceptos_vistos']))
    with col3:
        st.metric("✅ Quizzes Completados", len(progreso['quizzes_completados']))
    with col4:
        st.metric("⚖️ Casos Resueltos", len(progreso['casos_resueltos']))
    
    st.markdown(f"**Nivel Actual:** <span style='color:{color}; font-size:1.3rem; font-weight:bold;'>{nivel}</span>", unsafe_allow_html=True)
    
    # Barra de progreso hacia siguiente nivel
    puntos = progreso['puntos_totales']
    if puntos < 100:
        progreso_nivel = puntos / 100
        siguiente = "Aprendiz (100 pts)"
    elif puntos < 300:
        progreso_nivel = (puntos - 100) / 200
        siguiente = "Competente (300 pts)"
    elif puntos < 600:
        progreso_nivel = (puntos - 300) / 300
        siguiente = "Avanzado (600 pts)"
    elif puntos < 1000:
        progreso_nivel = (puntos - 600) / 400
        siguiente = "Experto (1000 pts)"
    else:
        progreso_nivel = 1.0
        siguiente = "¡Nivel Máximo!"
    
    st.progress(progreso_nivel)
    st.caption(f"Próximo nivel: {siguiente}")

def crear_grafico_cvp(etapa_seleccionada=None):
    """Crea gráfico interactivo del Ciclo de Vida del Producto"""
    x = np.linspace(0, 10, 100)
    
    # Curva de ventas
    ventas = np.concatenate([
        np.linspace(0, 30, 25),      # Introducción
        np.linspace(30, 80, 25),     # Crecimiento
        np.linspace(80, 85, 25) + np.random.normal(0, 2, 25),  # Madurez
        np.linspace(85, 20, 25)      # Declive
    ])
    
    # Curva de utilidades (retraso respecto a ventas)
    utilidades = np.concatenate([
        np.linspace(-20, 0, 25),     # Introducción (pérdidas)
        np.linspace(0, 60, 25),      # Crecimiento
        np.linspace(60, 65, 25),     # Madurez
        np.linspace(65, 10, 25)      # Declive
    ])
    
    fig = go.Figure()
    
    # Ventas
    fig.add_trace(go.Scatter(
        x=x, y=ventas,
        mode='lines',
        name='Ventas',
        line=dict(color='#3498db', width=3),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)'
    ))
    
    # Utilidades
    fig.add_trace(go.Scatter(
        x=x, y=utilidades,
        mode='lines',
        name='Utilidades',
        line=dict(color='#e74c3c', width=3, dash='dash')
    ))
    
    # Zonas de etapas
    etapas_info = [
        (0, 2.5, 'Introducción', '#e8f4f8'),
        (2.5, 5, 'Crecimiento', '#d4edda'),
        (5, 7.5, 'Madurez', '#fff3cd'),
        (7.5, 10, 'Declive', '#f8d7da')
    ]
    
    for inicio, fin, nombre, color in etapas_info:
        resaltar = etapa_seleccionada == nombre if etapa_seleccionada else False
        fig.add_vrect(
            x0=inicio, x1=fin,
            fillcolor=color,
            opacity=0.5 if resaltar else 0.2,
            line_width=2 if resaltar else 0,
            annotation_text=nombre if resaltar else "",
            annotation_position="top left"
        )
    
    fig.update_layout(
        title="Ciclo de Vida del Producto (CVP)",
        xaxis_title="Tiempo",
        yaxis_title="Ventas / Utilidades",
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(x=0.02, y=0.98)
    )
    
    return fig

# --- PÁGINA 1: INICIO Y DIAGNÓSTICO ---

def pagina_inicio():
    st.markdown("<h1 class='main-header'>🎯 Estrategia de Producto y Marca</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:1.2rem; color:#666;'>Plataforma Interactiva de Aprendizaje</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mostrar progreso si ya hay datos
    if st.session_state.progreso['puntos_totales'] > 0:
        with st.expander("📊 Ver Mi Progreso", expanded=False):
            mostrar_progreso_global()
        st.markdown("---")
    
    # Bienvenida
    st.markdown("""
    ### 👋 ¡Bienvenido a tu Estación de Aprendizaje!
    
    Esta plataforma te ayudará a dominar los conceptos fundamentales de **Estrategia de Producto y Marca** 
    desde la perspectiva del **Marketing 6.0**.
    
    #### 🎓 ¿Qué aprenderás?
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📚 Conceptos Fundamentales:**
        - Marketing 6.0 y creación de valor
        - Niveles y clasificación del producto
        - Ciclo de vida del producto (CVP)
        - Marca como activo estratégico
        - Identidad, imagen y equidad de marca
        """)
    
    with col2:
        st.markdown("""
        **🎯 Aplicaciones Estratégicas:**
        - Estrategias de marca y extensión
        - Posicionamiento efectivo
        - Innovación y desarrollo
        - Aspectos legales (caso Frisby)
        - Sostenibilidad y Marketing Real
        """)
    
    st.markdown("---")
    
    # Diagnóstico inicial
    if not st.session_state.diagnostico_completado:
        st.markdown("### 🔍 Diagnóstico Inicial")
        st.info("💡 **Comienza con un breve test** para identificar tus áreas de fortaleza y oportunidades de mejora.")
        
        if st.button("🚀 Iniciar Diagnóstico", type="primary", use_container_width=True):
            st.session_state.pagina_actual = "diagnostico"
            st.rerun()
    else:
        st.success("✅ **Diagnóstico completado.** Explora las secciones en el menú lateral.")
        
        # Recomendaciones personalizadas
        st.markdown("### 🎯 Recomendaciones Personalizadas")
        
        resultados = st.session_state.respuestas_diagnostico
        total = len(resultados)
        correctas = sum(resultados.values())
        porcentaje = (correctas / total * 100) if total > 0 else 0
        
        if porcentaje < 40:
            st.warning("""
            📚 **Comienza con los Fundamentos:**
            - Revisa la sección "Conceptos por Capítulo"
            - Comienza por Cap 1-3 para construir bases sólidas
            - Practica con el Quiz en modo básico
            """)
        elif porcentaje < 70:
            st.info("""
            🎯 **Refuerza y Profundiza:**
            - Explora el Simulador de CVP
            - Practica casos de decisión estratégica
            - Usa el Laboratorio de Conceptos para diferencias clave
            """)
        else:
            st.success("""
            ⭐ **¡Excelente base! Nivel Avanzado:**
            - Prueba el Quiz Adaptativo en modo avanzado
            - Resuelve todos los casos estratégicos
            - Crea tu marca en el Constructor
            """)

# --- PÁGINA 2: DIAGNÓSTICO ---

def pagina_diagnostico():
    st.markdown("<h1 class='main-header'>🔍 Diagnóstico Inicial</h1>", unsafe_allow_html=True)
    st.markdown("**Responde 5 preguntas para identificar tu nivel actual de conocimiento.**")
    
    st.markdown("---")
    
    preguntas_diagnostico = [
        {
            "pregunta": "¿Qué representa el Marketing 6.0?",
            "opciones": [
                "Marketing en redes sociales únicamente",
                "Convergencia de tecnología avanzada y humanismo",
                "Marketing tradicional mejorado",
                "Publicidad digital masiva"
            ],
            "correcta": 1
        },
        {
            "pregunta": "Los tres niveles del producto son:",
            "opciones": [
                "Precio, calidad y distribución",
                "Básico, real y aumentado",
                "Pequeño, mediano y grande",
                "Nacional, regional y global"
            ],
            "correcta": 1
        },
        {
            "pregunta": "¿Cuál es la diferencia clave entre identidad e imagen de marca?",
            "opciones": [
                "No hay diferencia real",
                "Identidad es interna (empresa), imagen es percepción (consumidor)",
                "Identidad es visual, imagen es conceptual",
                "Identidad es más importante que imagen"
            ],
            "correcta": 1
        },
        {
            "pregunta": "En la etapa de madurez del CVP, ¿qué sucede?",
            "opciones": [
                "Las ventas crecen aceleradamente",
                "Se lanza el producto por primera vez",
                "El mercado se satura y la competencia es intensa",
                "El producto desaparece del mercado"
            ],
            "correcta": 2
        },
        {
            "pregunta": "La equidad de marca (brand equity) se refiere a:",
            "opciones": [
                "El número de productos de la marca",
                "El valor adicional que la marca aporta al producto",
                "El logo de la empresa",
                "La antigüedad de la marca"
            ],
            "correcta": 1
        }
    ]
    
    # Formulario de diagnóstico
    with st.form("diagnostico_form"):
        respuestas = {}
        
        for i, item in enumerate(preguntas_diagnostico):
            st.markdown(f"**Pregunta {i+1}:** {item['pregunta']}")
            respuestas[i] = st.radio(
                f"Selecciona tu respuesta:",
                options=range(len(item['opciones'])),
                format_func=lambda x, opciones=item['opciones']: opciones[x],
                key=f"diag_{i}"
            )
            st.markdown("---")
        
        submitted = st.form_submit_button("📊 Ver Resultados", type="primary", use_container_width=True)
    
    # IMPORTANTE: El botón de volver debe estar FUERA del formulario
    if submitted:
        # Evaluar respuestas
        correctas_dict = {}
        total_correctas = 0
        
        for i, item in enumerate(preguntas_diagnostico):
            es_correcta = respuestas[i] == item['correcta']
            correctas_dict[i] = es_correcta
            if es_correcta:
                total_correctas += 1
        
        st.session_state.respuestas_diagnostico = correctas_dict
        st.session_state.diagnostico_completado = True
        
        # Mostrar resultados
        st.markdown("### 📊 Resultados del Diagnóstico")
        
        porcentaje = (total_correctas / len(preguntas_diagnostico)) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Respuestas Correctas", f"{total_correctas}/{len(preguntas_diagnostico)}")
        with col2:
            st.metric("Porcentaje", f"{porcentaje:.0f}%")
        with col3:
            if porcentaje >= 80:
                nivel = "⭐ Avanzado"
            elif porcentaje >= 60:
                nivel = "🎯 Intermedio"
            else:
                nivel = "🌱 Principiante"
            st.metric("Nivel Estimado", nivel)
        
        # Detalle por pregunta
        with st.expander("Ver detalle de respuestas"):
            for i, item in enumerate(preguntas_diagnostico):
                if correctas_dict[i]:
                    st.success(f"✅ Pregunta {i+1}: Correcta")
                else:
                    st.error(f"❌ Pregunta {i+1}: Incorrecta")
                    st.info(f"**Respuesta correcta:** {item['opciones'][item['correcta']]}")
        
        # Otorgar puntos
        actualizar_puntos(total_correctas * 10)
        
        st.success(f"🎉 ¡Diagnóstico completado! Has ganado {total_correctas * 10} puntos.")
    
    # Botón de volver FUERA del formulario
    st.markdown("---")
    if st.button("🏠 Volver al Inicio", key="volver_inicio_diagnostico"):
        st.session_state.pagina_actual = "inicio"
        st.rerun()

# --- PÁGINA 3: MAPA CONCEPTUAL ---

def pagina_mapa_conceptual():
    st.markdown("<h1 class='main-header'>🧭 Mapa Conceptual Interactivo</h1>", unsafe_allow_html=True)
    
    st.info("🗺️ **Visualiza la estructura completa del curso** y explora cada concepto.")
    
    st.markdown("---")
    
    # Crear mapa visual con expanders
    st.markdown("### 📚 Estructura del Conocimiento")
    
    categorias = {
        "🎯 Fundamentos del Marketing": ["Marketing 6.0", "Creación de Valor", "Orientación al Mercado"],
        "📦 El Producto Estratégico": ["Niveles del Producto", "Clasificación", "Producto como Experiencia"],
        "♻️ Ciclo de Vida": ["Introducción", "Crecimiento", "Madurez", "Declive"],
        "🏷️ La Marca como Activo": ["Identidad vs Imagen", "Equidad de Marca", "Reputación"],
        "🎨 Estrategias de Marca": ["Marca Individual", "Marca Corporativa", "Extensión", "Co-branding"],
        "🎯 Posicionamiento": ["Concepto", "Mapas Perceptuales", "Declaración"],
        "💡 Innovación": ["Tipos de Innovación", "Desarrollo NPD", "Sostenibilidad"],
        "⚖️ Aspectos Legales": ["Registro Marcario", "Protección", "Caso Frisby"]
    }
    
    # Mostrar categorías con conceptos
    for i, (categoria, conceptos) in enumerate(categorias.items()):
        with st.expander(f"**{categoria}**", expanded=(i==0)):
            cols = st.columns(len(conceptos))
            for j, concepto in enumerate(conceptos):
                with cols[j]:
                    # Verificar si fue visto
                    visto = concepto in st.session_state.progreso['conceptos_vistos']
                    icono = "✅" if visto else "⭕"
                    
                    if st.button(f"{icono} {concepto}", key=f"mapa_{concepto}", use_container_width=True):
                        st.session_state.concepto_seleccionado = concepto
                        st.session_state.progreso['conceptos_vistos'].add(concepto)
    
    # Mostrar concepto seleccionado
    if 'concepto_seleccionado' in st.session_state:
        st.markdown("---")
        st.markdown(f"### 💡 {st.session_state.concepto_seleccionado}")
        
        # Buscar definición en CONCEPTOS_CLAVE
        for cap, conceptos in CONCEPTOS_CLAVE.items():
            for nombre, datos in conceptos.items():
                if nombre == st.session_state.concepto_seleccionado or st.session_state.concepto_seleccionado in nombre:
                    st.markdown(f"**Definición:** {datos['definicion']}")
                    st.markdown(f"**Ejemplo:** {datos['ejemplo']}")
                    break
    
    # Indicador de progreso
    st.markdown("---")
    total_conceptos = sum(len(conceptos) for conceptos in categorias.values())
    vistos = len(st.session_state.progreso['conceptos_vistos'])
    progreso_pct = (vistos / total_conceptos) * 100
    
    st.markdown(f"**Progreso de exploración:** {vistos}/{total_conceptos} conceptos")
    st.progress(progreso_pct / 100)

# ... (continúa desde la parte anterior)

# --- PÁGINA 4: CONCEPTOS FLASH POR CAPÍTULO ---

def pagina_conceptos_flash():
    st.markdown("<h1 class='main-header'>📖 Biblioteca de Conceptos Flash</h1>", unsafe_allow_html=True)
    
    st.markdown("Explora los conceptos clave organizados por capítulos. Cada ficha incluye definición, ejemplo y pregunta de comprensión.")
    
    st.markdown("---")
    
    # Selector de capítulo
    capitulos = list(CONCEPTOS_CLAVE.keys())
    capitulo_seleccionado = st.selectbox("📚 Selecciona un Capítulo:", capitulos, key="selector_capitulo")
    
    st.markdown("---")
    
    # Mostrar conceptos del capítulo
    conceptos_capitulo = CONCEPTOS_CLAVE[capitulo_seleccionado]
    
    for nombre_concepto, datos in conceptos_capitulo.items():
        with st.expander(f"💡 **{nombre_concepto}**", expanded=False):
            
            # Definición
            st.markdown("<div class='concept-card'>", unsafe_allow_html=True)
            st.markdown(f"**📝 Definición:**")
            st.info(datos['definicion'])
            
            # Ejemplo
            st.markdown(f"**🎯 Ejemplo Aplicado:**")
            st.success(datos['ejemplo'])
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Pregunta de comprensión
            st.markdown("---")
            st.markdown("### ❓ Pregunta de Comprensión")
            
            pregunta_key = f"pregunta_{capitulo_seleccionado}_{nombre_concepto}"
            
            if pregunta_key not in st.session_state:
                st.session_state[pregunta_key] = {"respondida": False, "correcta": None}
            
            if not st.session_state[pregunta_key]["respondida"]:
                st.markdown(f"**{datos['pregunta']}**")
                
                respuesta = st.radio(
                    "Selecciona tu respuesta:",
                    options=range(len(datos['opciones'])),
                    format_func=lambda x: datos['opciones'][x],
                    key=f"radio_{pregunta_key}"
                )
                
                if st.button(f"Verificar Respuesta", key=f"btn_{pregunta_key}"):
                    es_correcta = respuesta == datos['respuesta_correcta']
                    st.session_state[pregunta_key]["respondida"] = True
                    st.session_state[pregunta_key]["correcta"] = es_correcta
                    
                    # Marcar concepto como visto
                    st.session_state.progreso['conceptos_vistos'].add(nombre_concepto)
                    
                    if es_correcta:
                        actualizar_puntos(10)
                    
                    st.rerun()
            
            else:
                # Mostrar resultado
                if st.session_state[pregunta_key]["correcta"]:
                    st.success(f"✅ **¡Correcto!** Has ganado 10 puntos.")
                    st.balloons()
                else:
                    st.error(f"❌ **Incorrecto.** La respuesta correcta es: {datos['opciones'][datos['respuesta_correcta']]}")
                    st.info("💡 Revisa nuevamente la definición y el ejemplo para reforzar el concepto.")
                
                if st.button(f"Reintentar", key=f"reintentar_{pregunta_key}"):
                    st.session_state[pregunta_key] = {"respondida": False, "correcta": None}
                    st.rerun()

# --- PÁGINA 5: SIMULADOR CVP ---

def pagina_simulador_cvp():
    st.markdown("<h1 class='main-header'>🎮 Simulador del Ciclo de Vida del Producto</h1>", unsafe_allow_html=True)
    
    st.markdown("Explora las etapas del CVP, analiza productos reales y aprende qué estrategias aplicar en cada fase.")
    
    st.markdown("---")
    
    # Selector de producto
    productos_ejemplo = {
        "iPhone (Apple)": {
            "etapa_actual": "Madurez",
            "descripcion": "Producto consolidado con alta penetración de mercado, competencia intensa y enfoque en innovación incremental.",
            "estrategias": [
                "Modificación del producto (nuevas versiones anuales)",
                "Diferenciación por ecosistema (Apple Watch, AirPods)",
                "Segmentación (iPhone SE, Pro, Pro Max)",
                "Programas de fidelización (Apple One)"
            ]
        },
        "Netflix": {
            "etapa_actual": "Madurez",
            "descripcion": "Líder en streaming pero con saturación en mercados clave y competencia creciente (Disney+, Prime Video).",
            "estrategias": [
                "Contenido original exclusivo",
                "Expansión a nuevos mercados geográficos",
                "Planes con publicidad (modificación del modelo)",
                "Control de compartición de cuentas"
            ]
        },
        "Automóvil Eléctrico": {
            "etapa_actual": "Crecimiento",
            "descripcion": "Tecnología en expansión con adopción creciente, múltiples competidores ingresando al mercado.",
            "estrategias": [
                "Ampliar red de carga (infraestructura)",
                "Mejorar autonomía de batería",
                "Reducir precios mediante economías de escala",
                "Diversificar modelos (SUV, sedán, deportivos)"
            ]
        },
        "Máquina de Escribir": {
            "etapa_actual": "Declive",
            "descripcion": "Tecnología obsoleta reemplazada por computadoras, ventas residuales en nichos específicos.",
            "estrategias": [
                "Enfoque en coleccionistas y mercado vintage",
                "Reducción de costos operativos",
                "Retiro progresivo del mercado masivo",
                "Pivote a productos relacionados (teclados mecánicos)"
            ]
        },
        "Realidad Virtual (VR)": {
            "etapa_actual": "Introducción",
            "descripcion": "Tecnología emergente con adopción inicial limitada, altos costos de desarrollo y educación del mercado.",
            "estrategias": [
                "Comunicación educativa sobre beneficios",
                "Alianzas con desarrolladores de contenido",
                "Demostraciones y pruebas en tiendas",
                "Reducción gradual de precios"
            ]
        }
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        producto_seleccionado = st.selectbox(
            "🎯 Selecciona un producto para analizar:",
            list(productos_ejemplo.keys())
        )
    
    with col2:
        etapa_resaltar = st.selectbox(
            "🔍 Resaltar etapa del CVP:",
            ["Ninguna", "Introducción", "Crecimiento", "Madurez", "Declive"]
        )
    
    # Mostrar gráfico CVP
    st.markdown("### 📊 Gráfico del Ciclo de Vida")
    fig_cvp = crear_grafico_cvp(etapa_resaltar if etapa_resaltar != "Ninguna" else None)
    st.plotly_chart(fig_cvp, use_container_width=True)
    
    # Información del producto
    st.markdown("---")
    st.markdown(f"### 📱 Análisis: **{producto_seleccionado}**")
    
    info_producto = productos_ejemplo[producto_seleccionado]
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.markdown(f"**Etapa Actual:**")
        st.markdown(f"<h2 style='color:#e74c3c;'>{info_producto['etapa_actual']}</h2>", unsafe_allow_html=True)
    
    with col_b:
        st.markdown(f"**Descripción:**")
        st.info(info_producto['descripcion'])
    
    st.markdown("**🎯 Estrategias Recomendadas:**")
    for estrategia in info_producto['estrategias']:
        st.markdown(f"- {estrategia}")
    
    # Quiz situacional
    st.markdown("---")
    st.markdown("### ❓ Quiz Situacional")
    
    quiz_cvp_key = f"quiz_cvp_{producto_seleccionado}"
    
    if quiz_cvp_key not in st.session_state:
        st.session_state[quiz_cvp_key] = False
    
    if not st.session_state[quiz_cvp_key]:
        st.markdown(f"**¿En qué etapa del CVP se encuentra {producto_seleccionado}?**")
        
        respuesta_cvp = st.radio(
            "Tu respuesta:",
            ["Introducción", "Crecimiento", "Madurez", "Declive"],
            key=f"radio_cvp_{producto_seleccionado}"
        )
        
        if st.button("Verificar", key=f"btn_cvp_{producto_seleccionado}"):
            if respuesta_cvp == info_producto['etapa_actual']:
                st.success(f"✅ ¡Correcto! {producto_seleccionado} está en etapa de {info_producto['etapa_actual']}.")
                actualizar_puntos(15)
                st.session_state[quiz_cvp_key] = True
                st.session_state.progreso['quizzes_completados'].add(quiz_cvp_key)
            else:
                st.error(f"❌ Incorrecto. La etapa correcta es: **{info_producto['etapa_actual']}**")
                st.info("💡 Revisa las características de cada etapa en el gráfico.")

# --- PÁGINA 6: CONSTRUCTOR DE MARCA ---

def pagina_constructor_marca():
    st.markdown("<h1 class='main-header'>🏗️ Constructor de Estrategia de Marca</h1>", unsafe_allow_html=True)
    
    st.markdown("Crea tu propia marca paso a paso y construye una estrategia coherente.")
    
    st.markdown("---")
    
    # Pestañas del proceso
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1️⃣ Identidad", 
        "2️⃣ Estrategia", 
        "3️⃣ Posicionamiento", 
        "4️⃣ Arquitectura",
        "5️⃣ Resumen"
    ])
    
    # TAB 1: IDENTIDAD
    with tab1:
        st.markdown("### 🎨 Define la Identidad de tu Marca")
        
        nombre_marca = st.text_input(
            "**Nombre de la Marca:**",
            value=st.session_state.marca_creada.get('nombre', ''),
            placeholder="Ej: EcoVida"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            categoria = st.selectbox(
                "**Categoría de Producto:**",
                ["Tecnología", "Alimentos", "Moda", "Salud", "Educación", "Entretenimiento", "Servicios"],
                index=["Tecnología", "Alimentos", "Moda", "Salud", "Educación", "Entretenimiento", "Servicios"].index(
                    st.session_state.marca_creada.get('categoria', 'Tecnología')
                )
            )
        
        with col2:
            proposito = st.text_input(
                "**Propósito de la Marca:**",
                value=st.session_state.marca_creada.get('proposito', ''),
                placeholder="Ej: Mejorar la salud del planeta"
            )
        
        valores = st.multiselect(
            "**Valores de Marca (selecciona 3-5):**",
            ["Innovación", "Sostenibilidad", "Calidad", "Accesibilidad", "Transparencia", 
             "Experiencia", "Tradición", "Tecnología", "Responsabilidad Social", "Autenticidad"],
            default=st.session_state.marca_creada.get('valores', [])
        )
        
        personalidad = st.text_area(
            "**Personalidad de Marca (¿Cómo hablaría tu marca?):**",
            value=st.session_state.marca_creada.get('personalidad', ''),
            placeholder="Ej: Cercana, inspiradora, comprometida con el cambio..."
        )
        
        if st.button("💾 Guardar Identidad", type="primary"):
            st.session_state.marca_creada.update({
                'nombre': nombre_marca,
                'categoria': categoria,
                'proposito': proposito,
                'valores': valores,
                'personalidad': personalidad
            })
            st.success("✅ Identidad guardada correctamente!")
            actualizar_puntos(20)
    
    # TAB 2: ESTRATEGIA
    with tab2:
        st.markdown("### 🎯 Define tu Estrategia de Marca")
        
        if 'nombre' not in st.session_state.marca_creada:
            st.warning("⚠️ Primero completa la Identidad de Marca en la pestaña anterior.")
        else:
            tipo_estrategia = st.radio(
                "**Tipo de Estrategia de Marca:**",
                [
                    "Marca Individual (cada producto tiene su propia marca)",
                    "Marca Corporativa (un solo nombre para todos los productos)",
                    "Marca Mixta (combinación de ambas)"
                ],
                index=[
                    "Marca Individual (cada producto tiene su propia marca)",
                    "Marca Corporativa (un solo nombre para todos los productos)",
                    "Marca Mixta (combinación de ambas)"
                ].index(st.session_state.marca_creada.get('tipo_estrategia', 
                    "Marca Individual (cada producto tiene su propia marca)")) if 'tipo_estrategia' in st.session_state.marca_creada else 0
            )
            
            st.info(f"""
            **📚 Explicación:**
            - **Marca Individual:** Cada producto tiene su propia identidad (ej: P&G con Pampers, Ariel, Gillette)
            - **Marca Corporativa:** Un nombre unifica todo (ej: Samsung, Sony)
            - **Marca Mixta:** Combina marca corporativa con sub-marcas (ej: Nestlé KitKat, Nestlé Nespresso)
            """)
            
            considera_extension = st.checkbox(
                "¿Consideras extensión de marca a futuro?",
                value=st.session_state.marca_creada.get('extension', False)
            )
            
            if considera_extension:
                categorias_extension = st.multiselect(
                    "**¿A qué categorías extenderías la marca?**",
                    ["Productos complementarios", "Nueva categoría relacionada", "Servicios asociados", 
                     "Mercado premium", "Mercado masivo"],
                    default=st.session_state.marca_creada.get('categorias_extension', [])
                )
            else:
                categorias_extension = []
            
            considera_cobranding = st.checkbox(
                "¿Considerarías alianzas de Co-branding?",
                value=st.session_state.marca_creada.get('cobranding', False)
            )
            
            if st.button("💾 Guardar Estrategia", type="primary"):
                st.session_state.marca_creada.update({
                    'tipo_estrategia': tipo_estrategia,
                    'extension': considera_extension,
                    'categorias_extension': categorias_extension,
                    'cobranding': considera_cobranding
                })
                st.success("✅ Estrategia guardada correctamente!")
                actualizar_puntos(20)
    
    # TAB 3: POSICIONAMIENTO
    with tab3:
        st.markdown("### 🎯 Construye tu Declaración de Posicionamiento")
        
        if 'nombre' not in st.session_state.marca_creada:
            st.warning("⚠️ Primero completa la Identidad de Marca.")
        else:
            st.info("""
            **📐 Estructura de una Declaración de Posicionamiento:**
            
            *"Para [PÚBLICO OBJETIVO] que [NECESIDAD/PROBLEMA], [MARCA] es [CATEGORÍA] 
            que [DIFERENCIACIÓN/BENEFICIO ÚNICO] a diferencia de [COMPETENCIA] porque [RAZÓN PARA CREER]."*
            """)
            
            publico = st.text_input(
                "**Público Objetivo:**",
                value=st.session_state.marca_creada.get('publico', ''),
                placeholder="Ej: jóvenes profesionales de 25-35 años"
            )
            
            necesidad = st.text_input(
                "**Necesidad/Problema:**",
                value=st.session_state.marca_creada.get('necesidad', ''),
                placeholder="Ej: buscan productos sostenibles sin sacrificar calidad"
            )
            
            diferenciacion = st.text_area(
                "**Diferenciación/Beneficio Único:**",
                value=st.session_state.marca_creada.get('diferenciacion', ''),
                placeholder="Ej: combina tecnología de punta con materiales 100% reciclados"
            )
            
            razon_creer = st.text_area(
                "**Razón para Creer:**",
                value=st.session_state.marca_creada.get('razon_creer', ''),
                placeholder="Ej: certificación ISO 14001 y transparencia total en la cadena de suministro"
            )
            
            # Generar declaración automáticamente
            if publico and necesidad and diferenciacion:
                nombre = st.session_state.marca_creada.get('nombre', '[MARCA]')
                categoria = st.session_state.marca_creada.get('categoria', '[CATEGORÍA]')
                
                declaracion = f"""
                **Tu Declaración de Posicionamiento:**
                
                *"Para {publico} que {necesidad}, {nombre} es {categoria} 
                que {diferenciacion}{' porque ' + razon_creer if razon_creer else ''}."*
                """
                
                st.success(declaracion)
            
            if st.button("💾 Guardar Posicionamiento", type="primary"):
                st.session_state.marca_creada.update({
                    'publico': publico,
                    'necesidad': necesidad,
                    'diferenciacion': diferenciacion,
                    'razon_creer': razon_creer
                })
                st.success("✅ Posicionamiento guardado correctamente!")
                actualizar_puntos(25)
    
    # TAB 4: ARQUITECTURA
    with tab4:
        st.markdown("### 🏛️ Define la Arquitectura de Marca")
        
        if 'nombre' not in st.session_state.marca_creada:
            st.warning("⚠️ Primero completa la Identidad de Marca.")
        else:
            st.info("""
            **📚 Tipos de Arquitectura de Marca:**
            - **Monolítica (Branded House):** Una marca única para todo (ej: FedEx)
            - **Respaldada (Endorsed):** Sub-marcas respaldadas por marca matriz (ej: Nestlé KitKat)
            - **Independiente (House of Brands):** Marcas totalmente independientes (ej: P&G)
            """)
            
            arquitectura = st.selectbox(
                "**Selecciona el tipo de Arquitectura:**",
                ["Monolítica (Branded House)", "Respaldada (Endorsed)", "Independiente (House of Brands)"],
                index=["Monolítica (Branded House)", "Respaldada (Endorsed)", "Independiente (House of Brands)"].index(
                    st.session_state.marca_creada.get('arquitectura', "Monolítica (Branded House)")
                ) if 'arquitectura' in st.session_state.marca_creada else 0
            )
            
            # Validación de coherencia
            tipo_estrategia = st.session_state.marca_creada.get('tipo_estrategia', '')
            
            coherencia = True
            mensaje_coherencia = ""
            
            if "Individual" in tipo_estrategia and arquitectura == "Monolítica (Branded House)":
                coherencia = False
                mensaje_coherencia = "⚠️ **Incoherencia detectada:** Seleccionaste estrategia de Marca Individual pero arquitectura Monolítica. Considera revisar tu estrategia."
            
            if "Corporativa" in tipo_estrategia and arquitectura == "Independiente (House of Brands)":
                coherencia = False
                mensaje_coherencia = "⚠️ **Incoherencia detectada:** Seleccionaste estrategia de Marca Corporativa pero arquitectura Independiente. Considera revisar tu estrategia."
            
            if not coherencia:
                st.warning(mensaje_coherencia)
            else:
                st.success("✅ Tu arquitectura es coherente con la estrategia de marca seleccionada.")
            
            num_lineas = st.slider(
                "**¿Cuántas líneas de producto planeas gestionar?**",
                min_value=1, max_value=10, 
                value=st.session_state.marca_creada.get('num_lineas', 3)
            )
            
            if st.button("💾 Guardar Arquitectura", type="primary"):
                st.session_state.marca_creada.update({
                    'arquitectura': arquitectura,
                    'num_lineas': num_lineas,
                    'coherencia_arquitectura': coherencia
                })
                st.success("✅ Arquitectura guardada correctamente!")
                actualizar_puntos(25)
    
    # TAB 5: RESUMEN
    with tab5:
        st.markdown("### 📋 Resumen de tu Estrategia de Marca")
        
        if 'nombre' not in st.session_state.marca_creada:
            st.warning("⚠️ Completa todas las secciones anteriores para ver el resumen.")
        else:
            marca = st.session_state.marca_creada
            
            # Tarjeta visual del resumen
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;'>
                <h1 style='text-align: center; margin: 0;'>{marca.get('nombre', 'Tu Marca')}</h1>
                <p style='text-align: center; font-size: 1.2rem; margin-top: 0.5rem;'>{marca.get('proposito', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎨 Identidad")
                st.markdown(f"**Categoría:** {marca.get('categoria', 'N/A')}")
                st.markdown(f"**Valores:** {', '.join(marca.get('valores', []))}")
                st.markdown(f"**Personalidad:** {marca.get('personalidad', 'N/A')}")
                
                st.markdown("#### 🎯 Estrategia")
                st.markdown(f"**Tipo:** {marca.get('tipo_estrategia', 'N/A').split('(')[0]}")
                st.markdown(f"**Extensión planificada:** {'Sí' if marca.get('extension') else 'No'}")
                if marca.get('extension'):
                    st.markdown(f"**Categorías de extensión:** {', '.join(marca.get('categorias_extension', []))}")
            
            with col2:
                st.markdown("#### 🏛️ Arquitectura")
                st.markdown(f"**Tipo:** {marca.get('arquitectura', 'N/A').split('(')[0]}")
                st.markdown(f"**Líneas de producto:** {marca.get('num_lineas', 'N/A')}")
                st.markdown(f"**Coherencia estratégica:** {'✅ Coherente' if marca.get('coherencia_arquitectura', True) else '⚠️ Revisar'}")
            
            st.markdown("---")
            st.markdown("#### 📐 Declaración de Posicionamiento")
            
            if marca.get('publico') and marca.get('necesidad') and marca.get('diferenciacion'):
                declaracion_final = f"""
                *"Para {marca.get('publico')} que {marca.get('necesidad')}, 
                {marca.get('nombre')} es {marca.get('categoria')} que {marca.get('diferenciacion')}
                {' porque ' + marca.get('razon_creer') if marca.get('razon_creer') else ''}."*
                """
                st.info(declaracion_final)
            else:
                st.warning("⚠️ Completa la sección de Posicionamiento para ver tu declaración.")
            
            st.markdown("---")
            
            # Evaluación de completitud
            campos_completados = sum([
                bool(marca.get('nombre')),
                bool(marca.get('proposito')),
                bool(marca.get('valores')),
                bool(marca.get('personalidad')),
                bool(marca.get('tipo_estrategia')),
                bool(marca.get('arquitectura')),
                bool(marca.get('publico')),
                bool(marca.get('diferenciacion'))
            ])
            
            completitud = (campos_completados / 8) * 100
            
            st.markdown(f"**Completitud de tu estrategia:** {completitud:.0f}%")
            st.progress(completitud / 100)
            
            if completitud == 100:
                st.success("🎉 ¡Felicitaciones! Has completado tu estrategia de marca de forma integral.")
                
                if st.button("🎓 Guardar como Caso de Estudio", type="primary"):
                    actualizar_puntos(50)
                    st.session_state.progreso['casos_resueltos'].add('constructor_marca')
                    st.balloons()
                    st.success("✅ Tu marca ha sido guardada. ¡Has ganado 50 puntos!")
            else:
                st.info("💡 Completa todas las secciones para obtener tu certificación de estrategia.")

# --- PÁGINA 7: CASOS DE DECISIÓN ---

def pagina_casos_decision():
    st.markdown("<h1 class='main-header'>⚖️ Casos de Decisión Estratégica</h1>", unsafe_allow_html=True)
    
    st.markdown("Analiza casos reales, toma decisiones estratégicas y aprende de las consecuencias.")
    
    st.markdown("---")
    
    # Selector de caso
    casos_disponibles = list(CASOS_ESTRATEGICOS.keys())
    nombres_casos = [CASOS_ESTRATEGICOS[caso]['titulo'] for caso in casos_disponibles]
    
    caso_seleccionado_idx = st.selectbox(
        "📚 Selecciona un caso para analizar:",
        range(len(nombres_casos)),
        format_func=lambda x: nombres_casos[x]
    )
    
    caso_key = casos_disponibles[caso_seleccionado_idx]
    caso = CASOS_ESTRATEGICOS[caso_key]
    
    st.markdown(f"### {caso['titulo']}")
    
    # Contexto del caso
    st.markdown("#### 📖 Contexto")
    st.info(caso['contexto'])
    
    st.markdown("---")
    
    # Estado del caso
    caso_state_key = f"caso_{caso_key}"
    if caso_state_key not in st.session_state:
        st.session_state[caso_state_key] = {"resuelto": False, "opcion_elegida": None}
    
    if not st.session_state[caso_state_key]["resuelto"]:
        st.markdown("#### 🤔 ¿Qué decisión tomarías?")
        
        for i, opcion in enumerate(caso['opciones']):
            if st.button(
                f"**Opción {i+1}:** {opcion['texto']}", 
                key=f"btn_{caso_key}_opcion_{i}",
                use_container_width=True
            ):
                st.session_state[caso_state_key]["resuelto"] = True
                st.session_state[caso_state_key]["opcion_elegida"] = i
                
                # Marcar caso como resuelto
                st.session_state.progreso['casos_resueltos'].add(caso_key)
                
                # Otorgar puntos
                if opcion['correcta']:
                    actualizar_puntos(30)
                else:
                    actualizar_puntos(10)  # Puntos por intentar
                
                st.rerun()
    
    else:
        # Mostrar resultado
        opcion_elegida = st.session_state[caso_state_key]["opcion_elegida"]
        opcion = caso['opciones'][opcion_elegida]
        
        st.markdown("---")
        st.markdown("#### 📊 Resultado de tu Decisión")
        
        if opcion['correcta']:
            st.success(f"✅ **Decisión Estratégica Adecuada**")
            st.markdown(f"**Opción elegida:** {opcion['texto']}")
            st.markdown(f"**Consecuencia:** {opcion['consecuencia']}")
            st.info(f"💡 **Aprendizaje:** {opcion['aprendizaje']}")
        else:
            st.warning(f"⚠️ **Decisión con Riesgos Significativos**")
            st.markdown(f"**Opción elegida:** {opcion['texto']}")
            st.markdown(f"**Consecuencia:** {opcion['consecuencia']}")
            st.error(f"❌ **Aprendizaje:** {opcion['aprendizaje']}")
        
        st.markdown("---")
        st.markdown("#### 🎓 Lección Final del Caso")
        st.info(caso['leccion_final'])
        
        if st.button("🔄 Intentar con otro caso", key=f"reset_{caso_key}"):
            st.session_state[caso_state_key] = {"resuelto": False, "opcion_elegida": None}
            st.rerun()

# --- PÁGINA 8: LABORATORIO DE CONCEPTOS ---

def pagina_laboratorio_conceptos():
    st.markdown("<h1 class='main-header'>🔬 Laboratorio de Conceptos</h1>", unsafe_allow_html=True)
    
    st.markdown("Comprende las diferencias clave entre conceptos que suelen confundirse.")
    
    st.markdown("---")
    
    # Comparaciones clave
    comparaciones = {
        "Identidad vs Imagen vs Reputación": {
            "conceptos": ["Identidad de Marca", "Imagen de Marca", "Reputación de Marca"],
            "definiciones": [
                "Cómo la empresa define y comunica quién es la marca (construcción interna y deliberada)",
                "Percepción que los consumidores tienen de la marca basada en experiencias e interacciones",
                "Resultado acumulado de percepciones en el tiempo, integra confianza y comportamiento ético"
            ],
            "control": ["Alto (empresa)", "Medio (influenciable)", "Bajo (largo plazo)"],
            "ejemplo": [
                "Nike define su identidad como 'inspiración atlética e innovación'",
                "Los consumidores perciben a Nike como 'marca deportiva premium y motivacional'",
                "Nike tiene reputación de innovación pero controversias laborales en su historia"
            ]
        },
        
        "Producto Básico vs Real vs Aumentado": {
            "conceptos": ["Producto Básico", "Producto Real", "Producto Aumentado"],
            "definiciones": [
                "Beneficio esencial que el consumidor busca satisfacer",
                "Atributos tangibles e intangibles: calidad, diseño, marca, empaque",
                "Servicios adicionales y experiencias complementarias que agregan valor"
            ],
            "ejemplo": [
                "Hotel: alojamiento",
                "Hotel: habitación limpia, diseño moderno, marca reconocida, Wi-Fi",
                "Hotel: spa, concierge 24/7, check-out tardío, programa de lealtad"
            ],
            "importancia": [
                "Define la necesidad a satisfacer",
                "Diferenciación competitiva principal",
                "Fidelización y ventaja sostenible"
            ]
        },
        
        "Extensión de Línea vs Extensión de Marca": {
            "conceptos": ["Extensión de Línea", "Extensión de Marca"],
            "definiciones": [
                "Nuevas versiones de un producto dentro de la MISMA categoría",
                "Aplicar marca existente a productos en NUEVA categoría"
            ],
            "riesgo": ["Bajo (mismo mercado)", "Alto (puede diluir marca)"],
            "ejemplo": [
                "Coca-Cola → Coca-Cola Zero, Coca-Cola Light (misma categoría: bebidas)",
                "Dove jabón → Dove shampoo (nueva categoría: cuidado capilar)"
            ],
            "ventaja": [
                "Satisface diferentes segmentos sin crear nueva marca",
                "Aprovecha equidad de marca para entrar a nuevos mercados"
            ]
        },
        
        "Marca Individual vs Corporativa": {
            "conceptos": ["Marca Individual", "Marca Corporativa"],
            "definiciones": [
                "Cada producto tiene su propia marca independiente",
                "Un solo nombre/marca para todos los productos"
            ],
            "ventaja": [
                "Posicionamientos diferenciados; fracaso no afecta portafolio",
                "Reconocimiento unificado; menores costos de marketing"
            ],
            "desventaja": [
                "Mayores costos de desarrollo y comunicación por marca",
                "Crisis en un producto afecta toda la organización"
            ],
            "ejemplo": [
                "P&G: Pampers, Ariel, Gillette, Oral-B (marcas independientes)",
                "Samsung: Samsung TV, Samsung Galaxy, Samsung Electrodomésticos"
            ]
        }
    }
    
    # Selector de comparación
    comparacion_seleccionada = st.selectbox(
        "🔍 Selecciona una comparación:",
        list(comparaciones.keys())
    )
    
    datos = comparaciones[comparacion_seleccionada]
    
    st.markdown(f"### {comparacion_seleccionada}")
    
    # Crear tabla comparativa
    df_comparacion = pd.DataFrame(datos)
    
    st.table(df_comparacion)
    
    st.markdown("---")
    
    # Quiz de diferenciación
    st.markdown("#### ❓ Quiz de Diferenciación")
    
    quiz_lab_key = f"quiz_lab_{comparacion_seleccionada}"
    
    if quiz_lab_key not in st.session_state:
        st.session_state[quiz_lab_key] = False
    
    if not st.session_state[quiz_lab_key]:
        # Generar pregunta según la comparación
        if comparacion_seleccionada == "Identidad vs Imagen vs Reputación":
            st.markdown("**¿Cuál concepto está más bajo el control de la empresa?**")
            opciones_quiz = ["Identidad de Marca", "Imagen de Marca", "Reputación de Marca"]
            correcta_quiz = 0
            explicacion_quiz = "La identidad es construcción interna y deliberada de la empresa, mientras que imagen y reputación dependen de percepciones externas."
        
        elif comparacion_seleccionada == "Producto Básico vs Real vs Aumentado":
            st.markdown("**¿En qué nivel del producto se encuentran los servicios postventa?**")
            opciones_quiz = ["Producto Básico", "Producto Real", "Producto Aumentado"]
            correcta_quiz = 2
            explicacion_quiz = "Los servicios postventa son parte del producto aumentado, que incluye beneficios adicionales que complementan la oferta."
        
        elif comparacion_seleccionada == "Extensión de Línea vs Extensión de Marca":
            st.markdown("**Dove lanzando shampoo después de vender jabón es un ejemplo de:**")
            opciones_quiz = ["Extensión de Línea", "Extensión de Marca", "Co-branding", "Marca Individual"]
            correcta_quiz = 1
            explicacion_quiz = "Es extensión de marca porque Dove entra a una NUEVA categoría (cuidado capilar) usando su marca existente de jabones."
        
        else:  # Marca Individual vs Corporativa
            st.markdown("**P&G gestionando Pampers, Ariel y Gillette como marcas separadas es un ejemplo de:**")
            opciones_quiz = ["Marca Corporativa", "Marca Individual", "Extensión de Marca", "Co-branding"]
            correcta_quiz = 1
            explicacion_quiz = "P&G usa estrategia de marcas individuales: cada producto tiene su propia identidad independiente."
        
        respuesta_lab = st.radio(
            "Tu respuesta:",
            options=range(len(opciones_quiz)),
            format_func=lambda x: opciones_quiz[x],
            key=f"radio_{quiz_lab_key}"
        )
        
        if st.button("Verificar", key=f"btn_{quiz_lab_key}"):
            if respuesta_lab == correcta_quiz:
                st.success(f"✅ ¡Correcto! {explicacion_quiz}")
                actualizar_puntos(15)
                st.session_state[quiz_lab_key] = True
                st.session_state.progreso['quizzes_completados'].add(quiz_lab_key)
            else:
                st.error(f"❌ Incorrecto. {explicacion_quiz}")
                st.info("💡 Revisa nuevamente la tabla comparativa.")

# --- PÁGINA 9: QUIZ ADAPTATIVO ---

def pagina_quiz_adaptativo():
    st.markdown("<h1 class='main-header'>🧪 Quiz Adaptativo</h1>", unsafe_allow_html=True)
    
    st.markdown("El quiz adapta su dificultad según tus respuestas. ¡Demuestra tu conocimiento!")
    
    st.markdown("---")
    
    # Selector de nivel inicial
    if 'quiz_adaptativo_iniciado' not in st.session_state:
        st.session_state.quiz_adaptativo_iniciado = False
        st.session_state.quiz_adaptativo_nivel = "basico"
        st.session_state.quiz_adaptativo_preguntas_respondidas = []
        st.session_state.quiz_adaptativo_correctas = 0
        st.session_state.quiz_adaptativo_pregunta_actual = None
    
    if not st.session_state.quiz_adaptativo_iniciado:
        st.markdown("### 🎯 Selecciona el nivel de dificultad inicial")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌱 Básico", use_container_width=True):
                st.session_state.quiz_adaptativo_nivel = "basico"
                st.session_state.quiz_adaptativo_iniciado = True
                st.rerun()
        
        with col2:
            if st.button("📚 Intermedio", use_container_width=True):
                st.session_state.quiz_adaptativo_nivel = "intermedio"
                st.session_state.quiz_adaptativo_iniciado = True
                st.rerun()
        
        with col3:
            if st.button("⭐ Avanzado", use_container_width=True):
                st.session_state.quiz_adaptativo_nivel = "avanzado"
                st.session_state.quiz_adaptativo_iniciado = True
                st.rerun()
        
        st.info("💡 El sistema ajustará automáticamente la dificultad según tu desempeño.")
    
    else:
        # Mostrar progreso
        total_respondidas = len(st.session_state.quiz_adaptativo_preguntas_respondidas)
        correctas = st.session_state.quiz_adaptativo_correctas
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Preguntas Respondidas", total_respondidas)
        with col2:
            st.metric("Respuestas Correctas", correctas)
        with col3:
            porcentaje = (correctas / total_respondidas * 100) if total_respondidas > 0 else 0
            st.metric("Porcentaje de Acierto", f"{porcentaje:.0f}%")
        
        st.markdown(f"**Nivel Actual:** {st.session_state.quiz_adaptativo_nivel.upper()}")
        
        st.markdown("---")
        
        # Seleccionar pregunta si no hay una actual
        if st.session_state.quiz_adaptativo_pregunta_actual is None:
            nivel = st.session_state.quiz_adaptativo_nivel
            preguntas_disponibles = [p for p in BANCO_PREGUNTAS[nivel] 
                                    if p['pregunta'] not in st.session_state.quiz_adaptativo_preguntas_respondidas]
            
            if not preguntas_disponibles:
                st.success("🎉 ¡Has completado todas las preguntas de este nivel!")
                
                if nivel == "basico":
                    st.info("💡 Puedes continuar con el nivel Intermedio.")
                    if st.button("▶️ Pasar a Intermedio"):
                        st.session_state.quiz_adaptativo_nivel = "intermedio"
                        st.rerun()
                
                elif nivel == "intermedio":
                    st.info("💡 Puedes continuar con el nivel Avanzado.")
                    if st.button("▶️ Pasar a Avanzado"):
                        st.session_state.quiz_adaptativo_nivel = "avanzado"
                        st.rerun()
                
                else:
                    st.balloons()
                    st.success("🏆 ¡Felicitaciones! Has completado todos los niveles del quiz.")
                    actualizar_puntos(100)
                
                if st.button("🔄 Reiniciar Quiz"):
                    st.session_state.quiz_adaptativo_iniciado = False
                    st.session_state.quiz_adaptativo_preguntas_respondidas = []
                    st.session_state.quiz_adaptativo_correctas = 0
                    st.session_state.quiz_adaptativo_pregunta_actual = None
                    st.rerun()
                
                return
            
            # Seleccionar pregunta aleatoria
            st.session_state.quiz_adaptativo_pregunta_actual = random.choice(preguntas_disponibles)
        
        # Mostrar pregunta actual
        pregunta = st.session_state.quiz_adaptativo_pregunta_actual
        
        st.markdown(f"### ❓ {pregunta['pregunta']}")
        st.caption(f"📚 Tema: {pregunta['tema']}")
        
        respuesta_usuario = st.radio(
            "Selecciona tu respuesta:",
            options=range(len(pregunta['opciones'])),
            format_func=lambda x: pregunta['opciones'][x],
            key="radio_quiz_adaptativo"
        )
        
        col_a, col_b = st.columns([1, 3])
        
        with col_a:
            if st.button("✅ Responder", type="primary", use_container_width=True):
                # Evaluar respuesta
                es_correcta = respuesta_usuario == pregunta['correcta']
                
                st.session_state.quiz_adaptativo_preguntas_respondidas.append(pregunta['pregunta'])
                
                if es_correcta:
                    st.session_state.quiz_adaptativo_correctas += 1
                    st.success(f"✅ ¡Correcto! {pregunta['explicacion']}")
                    
                    # Aumentar nivel si tiene buen desempeño
                    if st.session_state.quiz_adaptativo_correctas % 3 == 0:
                        if st.session_state.quiz_adaptativo_nivel == "basico":
                            st.session_state.quiz_adaptativo_nivel = "intermedio"
                            st.info("⬆️ ¡Nivel aumentado a INTERMEDIO!")
                        elif st.session_state.quiz_adaptativo_nivel == "intermedio":
                            st.session_state.quiz_adaptativo_nivel = "avanzado"
                            st.info("⬆️ ¡Nivel aumentado a AVANZADO!")
                    
                    actualizar_puntos(10 + (5 * ["basico", "intermedio", "avanzado"].index(st.session_state.quiz_adaptativo_nivel)))
                
                else:
                    st.error(f"❌ Incorrecto. {pregunta['explicacion']}")
                    st.info(f"💡 La respuesta correcta era: **{pregunta['opciones'][pregunta['correcta']]}**")
                    
                    # Bajar nivel si tiene mal desempeño
                    total = len(st.session_state.quiz_adaptativo_preguntas_respondidas)
                    if total >= 3:
                        porcentaje_actual = st.session_state.quiz_adaptativo_correctas / total
                        if porcentaje_actual < 0.5:
                            if st.session_state.quiz_adaptativo_nivel == "avanzado":
                                st.session_state.quiz_adaptativo_nivel = "intermedio"
                                st.warning("⬇️ Nivel ajustado a INTERMEDIO para reforzar conceptos.")
                            elif st.session_state.quiz_adaptativo_nivel == "intermedio":
                                st.session_state.quiz_adaptativo_nivel = "basico"
                                st.warning("⬇️ Nivel ajustado a BÁSICO para reforzar fundamentos.")
                
                # Limpiar pregunta actual para cargar siguiente
                st.session_state.quiz_adaptativo_pregunta_actual = None
                
                st.rerun()

# --- PÁGINA 10: PANEL DE REPASO ---

def pagina_panel_repaso():
    st.markdown("<h1 class='main-header'>📊 Panel de Repaso Final</h1>", unsafe_allow_html=True)
    
    st.markdown("Revisa todos los conceptos clave y evalúa tu dominio antes del examen.")
    
    st.markdown("---")
    
    # Tabs para organizar
    tab1, tab2, tab3 = st.tabs(["📚 Resumen Ejecutivo", "🔍 Glosario", "📝 Generador de Examen"])
    
    # TAB 1: RESUMEN EJECUTIVO
    with tab1:
        st.markdown("### 📚 Resumen Ejecutivo por Capítulo")
        
        resumenes = {
            "Marketing 6.0 y Valor": """
            - **Marketing 6.0:** Convergencia de tecnología (IA, big data) con humanismo y sostenibilidad
            - **Creación de Valor:** Proceso de ofrecer beneficios que satisfacen necesidades del consumidor
            - **Orientación al Mercado:** Capacidad de identificar y satisfacer necesidades mejor que competencia
            - **Marketing Relacional:** Construcción de relaciones duraderas, no solo transacciones
            """,
            
            "Producto Estratégico": """
            - **Niveles:** Básico (beneficio esencial), Real (atributos), Aumentado (servicios adicionales)
            - **Clasificación:** Conveniencia, Comparación, Especialidad, No buscados
            - **Producto como Experiencia:** El valor incluye dimensiones funcionales, emocionales y simbólicas
            - **Implicación:** El producto materializa la propuesta de valor de la empresa
            """,
            
            "Ciclo de Vida del Producto": """
            - **Introducción:** Ventas bajas, altos costos, comunicación informativa, generar conocimiento
            - **Crecimiento:** Ventas aumentan, competencia entra, mejoras del producto, expansión distribución
            - **Madurez:** Saturación, competencia intensa, defensa de participación, modificaciones
            - **Declive:** Ventas bajan, decidir mantener/modificar/eliminar, enfoque en nichos
            - **Clave:** Ajustar marketing mix según etapa actual
            """,
            
            "Marca como Activo": """
            - **Identidad:** Cómo la empresa define la marca (interno)
            - **Imagen:** Cómo el consumidor percibe la marca (externo)
            - **Reputación:** Percepción acumulada en el tiempo (credibilidad y ética)
            - **Equidad de Marca:** Valor adicional que aporta la marca más allá de atributos funcionales
            - **Modelos:** Aaker (activos/pasivos) y Keller (resonancia de marca)
            """,
            
            "Estrategias de Marca": """
            - **Individual:** Cada producto con marca propia (reduce riesgo, altos costos)
            - **Corporativa:** Un nombre para todo (reconocimiento, crisis afecta a todos)
            - **Extensión de Línea:** Nuevas versiones en misma categoría
            - **Extensión de Marca:** Marca existente en nueva categoría (riesgo de dilución)
            - **Co-branding:** Alianza entre marcas para combinar fortalezas
            """,
            
            "Posicionamiento": """
            - **Concepto:** Lugar que ocupa producto/marca en mente del consumidor vs competencia
            - **No es solo comunicación:** Es diseño integral de oferta e imagen
            - **Declaración:** Para [público] que [necesidad], [marca] es [categoría] que [diferenciación]
            - **Herramientas:** Mapas perceptuales para visualizar posicionamiento
            - **Errores:** Sobre-posicionamiento, sub-posicionamiento, confusión, dudas
            """,
            
            "Aspectos Legales (Caso Frisby)": """
            - **Registro Marcario:** Protección legal del nombre, símbolo y elementos de marca
            - **Lección Frisby:** Planificar registro internacional desde inicio, vigilancia constante
            - **Protección:** El registro debe ir acompañado de uso real en mercados
            - **Riesgo:** Marca es activo vulnerable sin gestión legal-estratégica integrada
            - **Colombia:** Registro ante SIC (Superintendencia de Industria y Comercio)
            """
        }
        
        for titulo, contenido in resumenes.items():
            with st.expander(f"**{titulo}**"):
                st.markdown(contenido)
    
    # TAB 2: GLOSARIO
    with tab2:
        st.markdown("### 🔍 Glosario Interactivo")
        
        glosario = {
            "Brand Equity (Equidad de Marca)": "Valor adicional que la marca aporta al producto más allá de sus características funcionales.",
            "Co-branding": "Estrategia de asociación entre dos o más marcas para desarrollo o comercialización de producto/servicio.",
            "Ciclo de Vida del Producto (CVP)": "Modelo que describe las etapas por las que atraviesa un producto: introducción, crecimiento, madurez y declive.",
            "Extensión de Línea": "Introducción de nuevas versiones de un producto dentro de la misma categoría.",
            "Extensión de Marca": "Aplicación de una marca existente a nuevos productos o categorías diferentes.",
            "Greenwashing": "Práctica engañosa de comunicar sostenibilidad ambiental falsa o exagerada.",
            "Identidad de Marca": "Forma en que la empresa define y comunica quién es la marca (construcción interna).",
            "Imagen de Marca": "Percepción que los consumidores tienen de la marca basada en experiencias.",
            "Marketing 6.0": "Evolución del marketing que integra tecnología avanzada con humanismo y sostenibilidad.",
            "Marca Corporativa": "Estrategia donde un solo nombre/marca unifica todos los productos de la empresa.",
            "Marca Individual": "Estrategia donde cada producto tiene su propia marca independiente.",
            "Posicionamiento": "Lugar que ocupa un producto o marca en la mente del consumidor en relación con competidores.",
            "Producto Aumentado": "Nivel del producto que incluye servicios adicionales y experiencias complementarias.",
            "Producto Básico": "Beneficio esencial que el consumidor busca al adquirir un producto.",
            "Producto Real": "Atributos tangibles e intangibles: calidad, diseño, marca, empaque.",
            "Propuesta de Valor": "Conjunto de beneficios que una empresa promete entregar al consumidor.",
            "Reputación de Marca": "Resultado acumulado de percepciones en el tiempo, integra confianza y comportamiento ético."
        }
        
        termino_buscar = st.text_input("🔎 Buscar término:", placeholder="Ej: Equidad")
        
        if termino_buscar:
            resultados = {k: v for k, v in glosario.items() if termino_buscar.lower() in k.lower()}
            if resultados:
                for termino, definicion in resultados.items():
                    st.markdown(f"**{termino}:** {definicion}")
            else:
                st.warning("No se encontraron resultados. Intenta con otro término.")
        else:
            # Mostrar todos
            for termino, definicion in sorted(glosario.items()):
                with st.expander(termino):
                    st.markdown(definicion)
    
    # TAB 3: GENERADOR DE EXAMEN
    with tab3:
        st.markdown("### 📝 Generador de Preguntas de Práctica")
        
        num_preguntas = st.slider("¿Cuántas preguntas quieres practicar?", 5, 20, 10)
        nivel_examen = st.selectbox("Nivel de dificultad:", ["Básico", "Intermedio", "Avanzado", "Mixto"])
        
        if st.button("🎲 Generar Examen de Práctica", type="primary"):
            st.markdown("---")
            st.markdown("### 📋 Tu Examen de Práctica")
            
            # Seleccionar preguntas
            if nivel_examen == "Mixto":
                pool_preguntas = []
                for nivel in ["basico", "intermedio", "avanzado"]:
                    pool_preguntas.extend(BANCO_PREGUNTAS[nivel])
            else:
                pool_preguntas = BANCO_PREGUNTAS[nivel_examen.lower()]
            
            preguntas_examen = random.sample(pool_preguntas, min(num_preguntas, len(pool_preguntas)))
            
            for i, pregunta in enumerate(preguntas_examen, 1):
                st.markdown(f"**{i}. {pregunta['pregunta']}** _(Tema: {pregunta['tema']})_")
                for j, opcion in enumerate(pregunta['opciones']):
                    st.markdown(f"   {chr(65+j)}. {opcion}")
                
                with st.expander("Ver respuesta"):
                    st.success(f"✅ Respuesta correcta: **{chr(65+pregunta['correcta'])}. {pregunta['opciones'][pregunta['correcta']]}**")
                    st.info(f"💡 {pregunta['explicacion']}")
                
                st.markdown("---")

# --- PÁGINA 11: MI PROGRESO ---

def pagina_mi_progreso():
    st.markdown("<h1 class='main-header'>🎓 Mi Progreso</h1>", unsafe_allow_html=True)
    
    mostrar_progreso_global()
    
    st.markdown("---")
    
    # Gráfico de progreso por área
    st.markdown("### 📊 Progreso por Área de Conocimiento")
    
    areas = {
        "Fundamentos": len([c for c in st.session_state.progreso['conceptos_vistos'] 
                           if any(x in c for x in ['Marketing', 'Valor', 'Orientación'])]),
        "Producto": len([c for c in st.session_state.progreso['conceptos_vistos'] 
                        if any(x in c for x in ['Producto', 'Niveles', 'Clasificación'])]),
        "Ciclo de Vida": len([c for c in st.session_state.progreso['conceptos_vistos'] 
                             if any(x in c for x in ['Ciclo', 'CVP', 'Etapa'])]),
        "Marca": len([c for c in st.session_state.progreso['conceptos_vistos'] 
                     if any(x in c for x in ['Marca', 'Identidad', 'Imagen', 'Equidad'])]),
        "Estrategia": len([c for c in st.session_state.progreso['conceptos_vistos'] 
                          if any(x in c for x in ['Estrategia', 'Extensión', 'Co-branding'])]),
        "Posicionamiento": len([c for c in st.session_state.progreso['conceptos_vistos'] 
                               if 'Posicion' in c])
    }
    
    fig_areas = go.Figure(data=[
        go.Bar(
            x=list(areas.keys()),
            y=list(areas.values()),
            marker=dict(color='#3498db'),
            text=list(areas.values()),
            textposition='auto'
        )
    ])
    
    fig_areas.update_layout(
        title="Conceptos Vistos por Área",
        xaxis_title="Área de Conocimiento",
        yaxis_title="Conceptos Vistos",
        height=400
    )
    
    st.plotly_chart(fig_areas, use_container_width=True)
    
    st.markdown("---")
    
    # Matriz de autoevaluación
    st.markdown("### ✅ Matriz de Autoevaluación")
    st.info("💡 Marca los conceptos que puedes explicar con tus propias palabras.")
    
    conceptos_clave_lista = [
        "Marketing 6.0", "Creación de Valor", "Niveles del Producto", 
        "Ciclo de Vida del Producto", "Identidad vs Imagen de Marca",
        "Equidad de Marca", "Extensión de Marca", "Posicionamiento",
        "Co-branding", "Producto Verde", "Caso Frisby"
    ]
    
    if 'autoevaluacion' not in st.session_state:
        st.session_state.autoevaluacion = {concepto: False for concepto in conceptos_clave_lista}
    
    col1, col2 = st.columns(2)
    
    for i, concepto in enumerate(conceptos_clave_lista):
        with col1 if i % 2 == 0 else col2:
            st.session_state.autoevaluacion[concepto] = st.checkbox(
                concepto,
                value=st.session_state.autoevaluacion[concepto],
                key=f"auto_{concepto}"
            )
    
    dominio = sum(st.session_state.autoevaluacion.values())
    porcentaje_dominio = (dominio / len(conceptos_clave_lista)) * 100
    
    st.markdown(f"**Dominio autoevaluado:** {dominio}/{len(conceptos_clave_lista)} conceptos ({porcentaje_dominio:.0f}%)")
    st.progress(porcentaje_dominio / 100)
    
    st.markdown("---")
    
    # Certificado de dominio
    st.markdown("### 🏆 Certificado de Dominio")
    
    progreso = st.session_state.progreso
    total_actividades = len(conceptos_clave_lista) + len(CASOS_ESTRATEGICOS) + 10  # Estimado
    completadas = len(progreso['conceptos_vistos']) + len(progreso['casos_resueltos']) + len(progreso['quizzes_completados'])
    porcentaje_actividades = (completadas / total_actividades) * 100
    
    if porcentaje_actividades >= 70:
        st.success("""
        🎉 **¡Felicitaciones!** Has alcanzado el nivel mínimo para el certificado.
        
        **Requisitos cumplidos:**
        - ✅ 70%+ de actividades completadas
        - ✅ Demostración de dominio conceptual
        """)
        
        if st.button("📜 Generar Certificado", type="primary"):
            st.markdown("---")
            
            # Certificado visual
            nivel_final, color_nivel = calcular_nivel_estudiante(progreso)
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 3rem; border-radius: 15px; color: white; text-align: center;'>
                <h1 style='font-size: 2.5rem; margin: 0;'>🎓 CERTIFICADO DE DOMINIO</h1>
                <h2 style='margin-top: 2rem;'>Estrategia de Producto y Marca</h2>
                <p style='font-size: 1.2rem; margin-top: 2rem;'>
                    Este certificado se otorga en reconocimiento al dominio de los conceptos fundamentales
                    y aplicaciones estratégicas del Marketing 6.0
                </p>
                <h3 style='margin-top: 2rem; font-size: 1.8rem;'>Nivel Alcanzado: {nivel_final}</h3>
                <p style='margin-top: 1rem;'>Puntos Totales: {progreso['puntos_totales']}</p>
                <p style='margin-top: 2rem; font-size: 0.9rem;'>
                    Fecha: {datetime.now().strftime("%d/%m/%Y")}<br>
                    Plataforma: Estación de Aprendizaje - Marketing Estratégico
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.balloons()
            actualizar_puntos(100)
    else:
        st.info(f"""
        📊 **Progreso actual:** {porcentaje_actividades:.1f}%
        
        **Para obtener el certificado necesitas:**
        - Completar al menos 70% de las actividades
        - Explorar más conceptos clave
        - Resolver casos estratégicos
        - Practicar con quizzes
        
        ¡Sigue adelante! 💪
        """)

# Continúa en la siguiente parte...
# ... (continúa desde la parte anterior)

# --- SISTEMA DE NAVEGACIÓN PRINCIPAL ---

# Inicializar página actual
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "inicio"

# --- SIDEBAR (MENÚ LATERAL) ---

with st.sidebar:
    st.markdown("### 🎯 Menú de Navegación")
    st.markdown("---")
    
    # Botón de inicio
    if st.button("🏠 Inicio", use_container_width=True, 
                 type="primary" if st.session_state.pagina_actual == "inicio" else "secondary"):
        st.session_state.pagina_actual = "inicio"
        st.rerun()
    
    # Diagnóstico
    if not st.session_state.diagnostico_completado:
        if st.button("🔍 Diagnóstico Inicial", use_container_width=True,
                     type="primary" if st.session_state.pagina_actual == "diagnostico" else "secondary"):
            st.session_state.pagina_actual = "diagnostico"
            st.rerun()
    
    st.markdown("---")
    st.markdown("**📚 Exploración**")
    
    if st.button("🧭 Mapa Conceptual", use_container_width=True,
                 type="primary" if st.session_state.pagina_actual == "mapa" else "secondary"):
        st.session_state.pagina_actual = "mapa"
        st.rerun()
    
    if st.button("📖 Conceptos Flash", use_container_width=True,
                 type="primary" if st.session_state.pagina_actual == "conceptos" else "secondary"):
        st.session_state.pagina_actual = "conceptos"
        st.rerun()
    
    st.markdown("---")
    st.markdown("**🎮 Interactivos**")
    
    if st.button("♻️ Simulador CVP", use_container_width=True,
                 type="primary" if st.session_state.pagina_actual == "simulador" else "secondary"):
        st.session_state.pagina_actual = "simulador"
        st.rerun()
    
    if st.button("🏗️ Constructor de Marca", use_container_width=True,
                 type="primary" if st.session_state.pagina_actual == "constructor" else "secondary"):
        st.session_state.pagina_actual = "constructor"
        st.rerun()
    
    if st.button("⚖️ Casos de Decisión", use_container_width=True,
                 type="primary" if st.session_state.pagina_actual == "casos" else "secondary"):
        st.session_state.pagina_actual = "casos"
        st.rerun()
    
    if st.button("🔬 Laboratorio de Conceptos", use_container_width=True,
                 type="primary" if st.session_state.pagina_actual == "laboratorio" else "secondary"):
        st.session_state.pagina_actual = "laboratorio"
        st.rerun()
    
    st.markdown("---")
    st.markdown("**🧪 Evaluación**")
    
    if st.button("🧪 Quiz Adaptativo", use_container_width=True,
                 type="primary" if st.session_state.pagina_actual == "quiz" else "secondary"):
        st.session_state.pagina_actual = "quiz"
        st.rerun()
    
    if st.button("📊 Panel de Repaso", use_container_width=True,
                 type="primary" if st.session_state.pagina_actual == "repaso" else "secondary"):
        st.session_state.pagina_actual = "repaso"
        st.rerun()
    
    st.markdown("---")
    
    if st.button("🎓 Mi Progreso", use_container_width=True,
                 type="primary" if st.session_state.pagina_actual == "progreso" else "secondary"):
        st.session_state.pagina_actual = "progreso"
        st.rerun()
    
    st.markdown("---")
    
    # Indicador de progreso en sidebar
    progreso = st.session_state.progreso
    nivel, color = calcular_nivel_estudiante(progreso)
    
    st.markdown(f"**Tu Nivel:** {nivel}")
    st.markdown(f"**Puntos:** {progreso['puntos_totales']}")
    
    # Mini badges
    if len(progreso['conceptos_vistos']) >= 10:
        st.markdown("🏅 Explorador")
    if len(progreso['quizzes_completados']) >= 5:
        st.markdown("🎯 Practicante")
    if len(progreso['casos_resueltos']) >= 2:
        st.markdown("⚖️ Estratega")
    if progreso['puntos_totales'] >= 500:
        st.markdown("⭐ Experto")
    
    st.markdown("---")
    
    # Botón de reinicio (con confirmación)
    if st.button("🔄 Reiniciar Progreso", use_container_width=True):
        if st.button("⚠️ Confirmar Reinicio", type="secondary"):
            st.session_state.progreso = {
                'conceptos_vistos': set(),
                'quizzes_completados': set(),
                'casos_resueltos': set(),
                'puntos_totales': 0,
                'nivel': 'Principiante'
            }
            st.session_state.diagnostico_completado = False
            st.session_state.respuestas_diagnostico = {}
            st.session_state.marca_creada = {}
            st.rerun()

# --- ENRUTADOR DE PÁGINAS ---

def main():
    """Función principal que enruta a la página correspondiente"""
    
    pagina = st.session_state.pagina_actual
    
    if pagina == "inicio":
        pagina_inicio()
    
    elif pagina == "diagnostico":
        pagina_diagnostico()
    
    elif pagina == "mapa":
        pagina_mapa_conceptual()
    
    elif pagina == "conceptos":
        pagina_conceptos_flash()
    
    elif pagina == "simulador":
        pagina_simulador_cvp()
    
    elif pagina == "constructor":
        pagina_constructor_marca()
    
    elif pagina == "casos":
        pagina_casos_decision()
    
    elif pagina == "laboratorio":
        pagina_laboratorio_conceptos()
    
    elif pagina == "quiz":
        pagina_quiz_adaptativo()
    
    elif pagina == "repaso":
        pagina_panel_repaso()
    
    elif pagina == "progreso":
        pagina_mi_progreso()
    
    else:
        st.error("⚠️ Página no encontrada")
        if st.button("🏠 Volver al Inicio"):
            st.session_state.pagina_actual = "inicio"
            st.rerun()
    
    # Footer común para todas las páginas
    st.markdown("---")
    st.markdown("""
    <div class='footer'>
        <p><strong>Realizado con ♥ para estudiantes de la Universidad Sergio Arboleda</strong></p>
        <p>Por: <strong>Mag. Diana Fruto</strong></p>
        <p style='font-size: 0.8rem; color: #999; margin-top: 1rem;'>
            📚 Material de apoyo académico | Marketing y Negocios Internacionales<br>
            📖 Basado en: Kotler, Keller, Aaker y principios del Marketing 6.0<br>
            🎯 Plataforma Interactiva de Aprendizaje - {}</p>
    </div>
    """.format(datetime.now().year), unsafe_allow_html=True)

# --- EJECUTAR APLICACIÓN ---

if __name__ == "__main__":
    main()





