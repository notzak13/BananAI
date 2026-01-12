

🍌 BananAI 

BananAI es un sistema diseñado para automatizar la cadena de suministro bananera. Utiliza Visión Artificial para la inspección de calidad y una arquitectura robusta de Programación Orientada a Objetos (POO) para gestionar inventarios, logística global y simulaciones financieras.

🏗️ Arquitectura del Sistema
El proyecto sigue un patrón de Arquitectura en Capas para garantizar el desacoplamiento y la escalabilidad:

Domain Layer (Models): Entidades puras (Banana, BananaBatch, Inventory) que encapsulan la lógica de negocio y el estado del producto.

Infrastructure Layer (Repository): Gestión de persistencia mediante el BatchRepository, encargado de la serialización/deserialización de datos en formato JSON.

Service Layer: Lógica especializada como PricingConfigService (estrategias de precios dinámicos) y SimulationService (generación de datos sintéticos).

Controller Layer: El OrderController actúa como mediador entre la interfaz y la lógica interna, asegurando transacciones atómicas.

Presentation Layer (UI): Dualidad de interfaces mediante Streamlit (Dashboard Ejecutivo) y una CLI (Bananazon) para simulación comercial.

🧠 Core Features (Ingeniería Destacada)
1. AI Inspection Pipeline
Implementación de un flujo de procesamiento de imágenes que utiliza el espacio de color HSV para la detección de madurez, eliminando la interferencia del brillo ambiental y garantizando una clasificación precisa en el campo.

2. Dynamic Pricing Strategy
Uso del patrón Strategy para calcular precios en tiempo real basados en:

Calidad (Confidence Score): Datos derivados de la inspección IA.

Tier del Cliente: Premium, Standard y Economic.

Logística: Costos de envío dinámicos según el destino global (China, USA, EU).

3. Transactional Integrity
El sistema genera un Manifiesto de Carga (.txt) y un Invoice (.json) por cada transacción, asegurando que el inventario se actualice de forma asíncrona y sin pérdida de datos.

📊 Diagrama de Clases (UML)
El diseño cumple con los estándares más altos de POO:

Composición: Entre OrderController y sus servicios.

Agregación: Entre Inventory y BananaBatch.

Herencia: En las estrategias de precios.

Code snippet

classDiagram
    Inventory "1" *-- "0..*" BananaBatch : contiene
    BananaBatch "1" *-- "1..*" BananaSample : composes
    OrderController o-- Inventory : manages
    OrderController o-- BatchRepository : uses
    PricingConfigService *-- PricingStrategy : strategy

    
🛠️ Instalación y Ejecución
Clonar el repositorio:

Bash

git clone https://github.com/notzak13/BananAI.git
Instalar dependencias:

Bash

pip install -r requirements.txt
Ejecutar el sistema:

Dashboard UI: streamlit run app.py

Simulación Comercial: python bananazon.py

Gestor de Lotes: python batch_manager.py

🧪 Validación y QA
El sistema ha sido sometido a pruebas de estrés para validar:

Manejo de Excepciones: Validación de entradas de peso y stocks negativos.

Persistencia: Integridad de los archivos JSON tras cierres inesperados.

Escalabilidad: Simulación de más de 100 órdenes simultáneas mediante el SimulationService.
