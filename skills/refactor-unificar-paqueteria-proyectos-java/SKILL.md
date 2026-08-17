---
name: refactor-unificar-paqueteria-proyectos-java
description: Revisa repositorios Java en src/main y src/test para detectar, traducir y unificar paquetes arquitectónicos al inglés mediante nombres canónicos fijos, con configuration y xml siempre singulares y las demás responsabilidades arquitectónicas siempre plurales, sin decidir por el número de clases y sin alterar nombres de dominio o contexto; exige una branch limpia antes de cualquier análisis o refactor.
---

# Unificar paquetes Java hacia una arquitectura común

Usar esta skill cuando se solicite un inventario o refactor de paquetes Java siguiendo una convención unificada de arquitectura screaming.

## Precondición obligatoria: branch limpia

No iniciar el inventario ni el refactor si el repositorio tiene cambios pendientes. Antes de cualquier análisis del repositorio ejecutar `git status --porcelain=v1` desde su raíz y exigir que no devuelva ninguna línea.

Se consideran cambios pendientes todos los ficheros modificados, preparados para commit, sin seguimiento, añadidos, eliminados, renombrados o en conflicto. Si la salida no está completamente vacía, detenerse inmediatamente: no escanear, no emitir inventario, no solicitar confirmación y no editar nada. No ocultar, descartar, sobrescribir, ignorar ni comitear automáticamente esos cambios.

Cuando se detecten cambios pendientes, informar únicamente de que la branch no está limpia, sin mostrar nombres de archivos, cantidades, tipos ni un resumen del estado. Utilizar este mensaje: «La branch no está limpia y no puede iniciarse el proceso de refactor. Debes eliminar los cambios locales o realizar el commit correspondiente. Una vez que la branch esté limpia, podrás avanzar con el refactor para evitar problemas de pérdida de código».

Después de que el usuario confirme un inventario, volver a ejecutar `git status --porcelain=v1` inmediatamente antes de modificar archivos. Si aparece cualquier cambio, abortar el refactor y exigir que la branch vuelva a estar limpia. Los únicos cambios permitidos después de comenzar un refactor autorizado serán los generados por la propia skill.

## Convención general

Inspeccionar tanto `src/main` como `src/test`, incluyendo todos los ficheros `.java` y sus declaraciones `package`. Usar `src/test` para conocer la presencia y aplicar el refactor de forma consistente.

La cantidad de clases es únicamente informativa. No usarla para decidir si un paquete debe ser singular o plural, ni sumar clases de `src/main` y `src/test` para resolver el nombre canónico. Si se informa el número de clases, mostrarlo por origen cuando exista el paquete en ambos: `N en main y M en test`; indicar también la presencia como `main`, `test` o `main y test`.

### Límite de la screaming architecture

Aplicar estas reglas únicamente a segmentos que expresen una responsabilidad arquitectónica. No traducir ni normalizar automáticamente segmentos de dominio, producto, cliente, origen, flujo o funcionalidad concreta. Por ejemplo, conservar `respuestalarga`, `respuestacorta`, `envios`, `gloval`, `clientes`, `orquestador`, `webclient`, `tasacion`, `solicitud`, `origengloval` y `origeneurocajarural`.

Un segmento protegido no impide analizar sus subpaquetes: conservar `respuestalarga`, pero revisar y normalizar `respuestalarga.mapeadores`, `respuestalarga.servicios`, `respuestalarga.component` o cualquier otro subpaquete arquitectónico reconocido.

No traducir, pluralizar ni singularizar segmentos no arquitectónicos que representen un formato, protocolo, tecnología, producto o concepto de dominio. Si su significado no es inequívoco, registrarlos como conflicto semántico y solicitar una decisión manual.

## Nombres arquitectónicos canónicos

Usar siempre nombres de paquete en inglés y minúsculas.

### Segmentos siempre singulares

Normalizar siempre estos segmentos al nombre indicado, independientemente del número de clases o de módulos:

- `configuration`, `configurations`, `configuracion` y `configuraciones` → `configuration`;
- `xml` y `xmls` → `xml`.

Una aplicación puede tener varias configuraciones por módulo, pero el ámbito de cada package de configuración se expresa en singular como `configuration`. `xml` identifica el ámbito del XML y, por tanto, siempre conserva ese nombre.

### Segmentos arquitectónicos siempre plurales

Normalizar siempre las variantes indicadas al nombre plural canónico, aunque el paquete contenga una sola clase:

- `annotation` / `annotations` → `annotations`;
- `bean` / `beans` → `beans`;
- `builder` / `builders` → `builders`;
- `component` / `components` → `components`;
- `constant` / `constants` → `constants`;
- `controller` / `controllers` → `controllers`;
- `conversion` / `conversions` → `conversions`;
- `dao` / `daos` → `daos`;
- `domain` / `domains` → `domains`;
- `dto` / `dtos` → `dtos`;
- `entity` / `entities` → `entities`;
- `enumeration` / `enumerations` → `enumerations`;
- `exception` / `exceptions` → `exceptions`;
- `helper` / `helpers` → `helpers`;
- `interceptor` / `interceptors` → `interceptors`;
- `mapper` / `mappers` → `mappers`;
- `repository` / `repositories` → `repositories`;
- `request` / `requests` → `requests`;
- `serializer` / `serializers` → `serializers`;
- `service` / `services` → `services`;
- `util` / `utils` → `utils`;
- `view` / `views` → `views`.

En particular, usar siempre `controllers`, `builders`, `views`, `daos`, `dtos`, `repositories`, `services`, `mappers` y `exceptions`, sin singularizarlos porque en ese momento tengan una sola clase.

### Variantes arquitectónicas en español

Traducir al nombre canónico inglés sin traducir nombres de dominio o contexto. Como mínimo, reconocer:

- `anotacion` / `anotaciones` → `annotations`;
- `ayudante` / `ayudantes` → `helpers`;
- `componente` / `componentes` → `components`;
- `configuracion` / `configuraciones` → `configuration`;
- `constante` / `constantes` → `constants`;
- `controlador` / `controladores` → `controllers`;
- `conversion` / `conversiones` → `conversions`;
- `entidad` / `entidades` → `entities`;
- `excepcion` / `excepciones` → `exceptions`;
- `mapeador` / `mapeadores` → `mappers`;
- `repositorio` / `repositorios` → `repositories`;
- `serializador` / `serializadores` → `serializers`;
- `servicio` / `servicios` → `services`;
- `utilidad` / `utilidades` → `utils`;
- `vista` / `vistas` → `views`.

No aplicar una traducción española no incluida cuando el segmento pueda ser un nombre de dominio, producto o contexto. En ese caso, tratarlo como posible conflicto semántico.

## Conflictos semánticos

Detectar como conflicto cualquier segmento no arquitectónico cuyo cambio de nombre pueda alterar el significado del paquete y no pueda resolverse con seguridad por su contexto.

No registrar como conflicto `configurations`, `configuracion`, `configuraciones` o `xmls`: sus transformaciones a `configuration` y `xml` son fijas. Tampoco registrar como conflicto las variantes singulares de los paquetes arquitectónicos reconocidos: deben normalizarse automáticamente a sus nombres plurales canónicos, sin considerar el número de clases.

Para cada conflicto, mostrar el prefijo completo hasta el segmento dudoso, las alternativas posibles, el número de clases por origen y la presencia en `main`, `test` o ambos. No incluir rutas descendientes completas y no aplicar el cambio automáticamente.

Usar una pregunta de decisión como: `Tengo dudas con esta paquetería, ¿cómo procedemos con «<paquete>»? ¿Mantenemos «<segmento actual>» o lo cambiamos a «<alternativa>»?`.

## Flujo obligatorio

1. Verificar la precondición de branch limpia con `git status --porcelain=v1`; si no está vacía, detenerse sin realizar ninguna otra acción de la skill.
2. Escanear `src/main` y `src/test` por separado. Preferir `scripts/scan_java_packages.py` para obtener declaraciones `package` únicas y el detalle de ficheros por paquete. Usar la cantidad de clases únicamente como dato informativo.
3. Emitir el inventario únicamente con estas cinco secciones, en este orden y sin introducciones, conclusiones, notas explicativas ni mensajes sobre prefijos protegidos:
   - `Traducciones al inglés`: segmentos arquitectónicos españoles que deben traducirse, con transformación exacta, número de clases por origen y presencia en `main`, `test` o ambos;
   - `Singulares que deben pluralizarse`: segmentos arquitectónicos ingleses singulares que deben adoptar su nombre plural canónico, independientemente del número de clases, con transformación exacta, número de clases por origen y presencia;
   - `Normalizaciones fijas`: `configurations` → `configuration` y `xmls` → `xml`, con transformación exacta, número de clases por origen y presencia;
   - `Conflictos semánticos`: segmentos no arquitectónicos cuyo nombre sea dudoso, con alternativas, número de clases por origen y presencia;
   - `Paquetes conformes`: paquetes arquitectónicos cuyo nombre ya coincide con el nombre canónico fijo, con número de clases por origen y presencia.
   Ordenar alfabéticamente cada sección por prefijo completo y escribir `Ninguno` cuando no haya entradas. No incluir rutas descendientes completas cuando los segmentos posteriores no sean el candidato detectado.
4. En las tres primeras secciones, cambiar únicamente el segmento final detectado: español → inglés, singular → plural canónico o alias fijo → nombre fijo. No modificar nombres protegidos de dominio/contexto ni palabras ambiguas. Si hay conflictos, terminar con una única línea de pregunta usando el formato `Tengo dudas con esta paquetería, ¿cómo procedemos? Indica para cada conflicto si se mantiene o qué nombre debe tener.` Si no hay conflictos, terminar con `¿Confirmas este inventario para aplicar el refactor?`.
5. Si el usuario corrige, elimina o resuelve entradas, volver a emitir las cinco secciones completas ya modificadas antes de solicitar confirmación de nuevo. No aplicar ningún conflicto hasta que el usuario haya indicado explícitamente su decisión y haya confirmado el inventario.
6. No mover ni editar archivos durante el inventario. Solo tras la autorización explícita del usuario y una nueva comprobación limpia de `git status --porcelain=v1`, aplicar el refactor en `main` y `test`: mover directorios, actualizar declaraciones `package`, imports, referencias totalmente cualificadas y cualquier configuración Java que apunte a esos paquetes.
7. Verificar después únicamente con búsquedas de los nombres antiguos y otras comprobaciones estáticas que no requieran compilación. No ejecutar el build ni los tests para ahorrar tokens. Al terminar el refactor, avisar al usuario de que debe ejecutar el build del proyecto, por ejemplo `./gradlew build`, y pedirle que comunique cualquier fallo para analizarlo y corregirlo. Recomendar que, al realizar el commit, utilice exactamente este título: «Refactor de paquetería con el uso de la skill /refactor-unificar-paqueteria-proyectos-java».

## Reglas para el refactor autorizado

- Hacer el cambio de forma consistente en producción y tests.
- Aplicar cada renombrado al segmento arquitectónico canónico y a todos sus subpaquetes, declaraciones `package` e imports descendientes, sin tocar el prefijo protegido de dominio/contexto.
- Normalizar siempre `configuration` y `xml` a sus formas singulares fijas.
- Normalizar siempre los segmentos arquitectónicos reconocidos a sus formas plurales canónicas, incluso cuando contengan una sola clase. No crear decisiones ni categorías basadas en cardinalidad.
- Aplicar los cambios de segmentos no arquitectónicos únicamente cuando el usuario haya confirmado explícitamente la transformación elegida para cada conflicto.
- Usar `git mv` o una operación equivalente preservando el historial cuando sea apropiado.
- No tocar nombres de clases, métodos o variables salvo que el cambio de paquete lo exija en una referencia cualificada.
- No trabajar sobre ficheros con modificaciones locales: validar la branch limpia antes de inspeccionar o editar el repositorio y volver a validarla antes del refactor autorizado.
- Antes de ejecutar cambios, mostrar el alcance final si la confirmación del usuario no identifica inequívocamente todos los paquetes.

## Recurso

`scripts/scan_java_packages.py` escanea declaraciones `package` en rutas proporcionadas, emite paquetes únicos y clasifica los segmentos según los nombres canónicos fijos. Usarlo como base objetiva del inventario y complementar con inspección de imports cuando sea necesario. El script no decide nombres por el número de clases.
