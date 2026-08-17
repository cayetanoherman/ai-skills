---
name: gloval-web-mantenimiento
description: Patrón estándar para web apps Gloval Java 8 (proyecto de referencia `/home/abraham/git/Mantenimiento`). Cubre estructura de JSPs sin scriptlets, clases Route por JSP, ViewModels por JSP, configuración vía `ApplicationProperties` + `ConfigLoaderListener`, claves en `ConstantsHelper`, y cache-busting de assets JS. Invocar al crear/editar `.jsp` en estos proyectos, al añadir una Route o ViewModel, al tocar `.properties` de la app, al modificar JS estáticos servidos por el WAR, o al hablar de "patrón Mantenimiento", "JSP Gloval", "Route+ViewModel".
---

# gloval-web-mantenimiento

Estándar de referencia para web apps Java 8 de Gloval. Proyecto base: `/home/abraham/git/Mantenimiento`.

---

## JSPs

- **Nada de scriptlets** `<% %>`, `<%= %>`, `<%! %>` — solo JSTL/EL.
- JSPs en `src/main/webapp/WEB-INF/views/` (acceso solo vía forward, nunca URL directa).
- En la cabecera: `<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>`.
- JS embebido: `var` → `const`/`let`.

---

## Routes (una por JSP)

- Paquete `<base>.routes`, clase `<NombreJSP>Route` (ej. `Aprovechamiento.jsp` → `AprovechamientoRoute.java`).
- Lombok `@Builder @Data @AllArgsConstructor @NoArgsConstructor(access=PRIVATE)`.
- **Muy sencilla**: solo sube el viewmodel a la request y hace forward. Nada de `setAttribute` sueltos para constantes/pies/config — todo eso va dentro del viewmodel.
- Método `navigate(HttpServletRequest, HttpServletResponse)`:
  - `request.setAttribute("model", model)`
  - `request.getRequestDispatcher(response.encodeURL("/WEB-INF/views/X.jsp")).forward(...)`.
- El atributo de request se llama **siempre `"model"`** (definido como `RequestAttribute.MODEL` en `ConstantsHelper`) — convención uniforme entre todas las JSPs para que su uso sea predecible.
- Uso desde el controlador:
  ```java
  XxxRoute.builder().model(viewmodel).build().navigate(req, resp);
  ```

---

## ViewModels

- Paquete `<base>.viewmodels`, clase `<NombreJSP>ViewModel` (mismo nombre que la página: `Aprovechamiento.jsp` → `AprovechamientoViewModel`).
- **Idealmente uno solo por JSP** que agrupe todo lo que la página necesita: datos del caso de uso + constantes/pies + valores de configuración (api keys, versiones de assets, etc.).
- Construcción vía static factory en el propio viewmodel (`MapasDocViewModel.from(Normalizada)`): la viewmodel sabe ensamblarse con sus constantes/config; el controller solo le pasa el dato de dominio.
- Lombok `@Data @Builder` (o `@Getter @Builder` si inmutable). Sin lógica de negocio.
- En la JSP, todo accede vía `${model.xxx}`. Nada de `${atributoSuelto}` salvo casos puntuales bien justificados.

---

## Configuración (`.properties`)

### Listener

`<base>.listeners.ConfigLoaderListener` con `@WebListener`:

- Carga `/data/informes/<app>/properties/<app>.properties` con `FileInputStream`.
- Llama `ApplicationProperties.initialize(props)`.
- Guarda también en `ServletContext` como `applicationProperties` (para JSP: `${applicationProperties['clave']}`).
- Configura Log4J leyendo `PropertyKey.LOG4J_CONFIG_FILE`.
- `contextDestroyed` llama `ApplicationProperties.destroy()`.

### Servicio

Clase estática `<base>.services.ApplicationProperties` (`@Log4j @NoArgsConstructor(PRIVATE)`):

- `initialize(Properties)`, `destroy()`, `isInitialized()`, `has(key)`.
- Getters por tipo con y sin default: `get`, `getInt`, `getLong`, `getFloat`, `getDouble`, `getBoolean`, `getBigInteger`, `getBigDecimal`, `getLocalDate`, `getLocalDateTime`, `getEnum`.

### `ConstantsHelper`

- Top-level: `APPLICATION_PROPERTIES_FILE = "/data/informes/<app>/properties/<app>.properties"`.
- Inner `ContextAttribute.APPLICATION_PROPERTIES = "applicationProperties"`.
- Inner `PropertyKey` con las claves del fichero.

---

## Cache-busting de assets JS

- Cuando modificas un `.js`, **bumpear** la versión que pasa por query string: `?v=YYYYMMDD-N`.
- La versión vive en `ConstantsHelper` (inner `AssetVersion`) y se expone como campo del viewmodel.
- La JSP la usa con `${model.imageCaptureJsVersion}` (o equivalente).
