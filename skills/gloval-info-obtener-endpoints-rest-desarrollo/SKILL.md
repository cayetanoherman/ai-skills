---
name: gloval-info-obtener-endpoints-rest-desarrollo
description: Resuelve automáticamente el puerto del entorno de desarrollo desde Gloval_Cloud.json y lista, a partir del repositorio Java actual, todos los endpoints REST expuestos por controllers o rutas REST, construyendo cada URL con http://devnext.gloval.internal:{puerto}. Si el proyecto no aparece en la configuración, solicita el puerto manualmente. Usar cuando se necesite un inventario de endpoints para realizar pruebas contra desarrollo.
---

# Obtener endpoints REST de desarrollo

## Resolución del puerto y flujo obligatorio

1. No solicitar el puerto en la primera respuesta. Resolverlo automáticamente antes de inspeccionar los endpoints.
2. Obtener el nombre del proyecto a partir del nombre del directorio raíz del repositorio actual. Normalizarlo para la comparación convirtiéndolo a minúsculas y eliminando todos los caracteres que no sean letras ASCII o números. Por ejemplo, `api-documentacion-caixabank` se compara como `apidocumentacioncaixabank`.
3. Leer `/home/cherman-businessgo-org/.codex/skills/gloval-info-obtener-endpoints-rest-desarrollo/json/Gloval_Cloud.json` y buscar una coincidencia exacta, una vez normalizada, en `variables[].name`. No usar coincidencias parciales.
4. Para la variable coincidente, extraer el puerto numérico de `variables[].value` y aceptar únicamente valores entre `1` y `65535`. Usar ese puerto para construir las URLs.
5. Si no existe una coincidencia exacta o la variable no contiene un puerto válido, detener el proceso y responder: `No encuentro el nombre del proyecto en el archivo de configuración Gloval_Cloud.json. Por favor, adjúntame el puerto del entorno de desarrollo.` En una respuesta posterior, aceptar únicamente un puerto numérico válido entre `1` y `65535`; si no es válido, repetir esa solicitud sin inspeccionar el repositorio.
6. Tras resolver o recibir el puerto, inspeccionar estáticamente el repositorio actual y únicamente sus fuentes de producción. No hacer peticiones HTTP al entorno: el puerto solo se utiliza para construir las URLs del inventario.
7. No ejecutar ninguna operación Git, incluyendo `git status`, `git diff`, `git log` o cualquier comando que cambie el estado del repositorio.
8. No editar, mover, crear ni eliminar archivos del repositorio. No solicitar autorización, confirmación ni cambios al usuario.
9. Devolver directamente la lista final de endpoints.

## Descubrimiento de rutas

Inspeccionar todos los ficheros Java de `src/main` (o el directorio equivalente de código de producción) y no limitar la búsqueda a nombres de fichero que contengan `Controller`. Considerar, como mínimo:

- clases anotadas con `@RestController`;
- clases anotadas con `@Controller` que expongan métodos `@ResponseBody`;
- `@RequestMapping` a nivel de clase y método;
- `@GetMapping`, `@PostMapping`, `@PutMapping`, `@PatchMapping`, `@DeleteMapping`, `@HeadMapping` y `@OptionsMapping`;
- rutas declarativas JAX-RS (`@Path` y anotaciones HTTP) y rutas funcionales Spring (`RouterFunction`, `route`, `coRouter`) si existen;
- mappings declarados en interfaces o clases base cuando el controller los herede.

Combinar siempre el prefijo de clase con cada ruta de método. Expandir arrays de rutas y todos los métodos HTTP declarados. Para cada endpoint identificar los parámetros de ruta, query, headers, cookies, formularios y cuerpos (`@RequestBody`), incluyendo nombre y tipo cuando estén disponibles. Para un cuerpo DTO, consultar su clase para enumerar sus campos si la información está en el repositorio. Marcar `ninguno` cuando no reciba parámetros.

Usar `scripts/list_rest_endpoints.py` como primera ayuda cuando sea aplicable:

```bash
python3 /home/cherman-businessgo-org/.codex/skills/gloval-info-obtener-endpoints-rest-desarrollo/scripts/list_rest_endpoints.py --root . --port <puerto-resuelto>
```

Complementar su resultado con búsquedas estáticas (`rg`) si hay anotaciones, herencia o routers que el script no pueda resolver. No ejecutar compilación ni tests.

## Construcción de las URLs

Construir cada URL con este prefijo exacto:

```text
http://devnext.gloval.internal:<puerto>
```

Después del puerto, añadir el `server.servlet.context-path` configurado para la aplicación, si existe, y a continuación la ruta REST resultante. Normalizar las barras para no producir `//`. Si no hay context path, añadir una única `/` antes de la ruta. Preferir la configuración activa `src/main/resources/application.properties`; consultar configuraciones de perfil solo si son necesarias para resolver la aplicación actual. No imprimir valores de credenciales ni otros secretos encontrados en propiedades.

## Descubrimiento de Swagger

Comprobar en los ficheros de configuración de producción y en las dependencias del proyecto si está habilitado Springdoc/OpenAPI o Swagger. Si se detecta, incluir siempre sus URLs en un bloque separado del inventario REST:

- Documentación OpenAPI JSON: usar `springdoc.api-docs.path` si está configurado; en otro caso, usar `/v3/api-docs`.
- Swagger UI: `/swagger-ui/index.html`.
- Ruta de compatibilidad de Swagger UI: `/swagger-ui.html`.

Aplicar a estas rutas el mismo prefijo de host, puerto y `server.servlet.context-path`, normalizando las barras. Indicar `parámetros: ninguno` en todas ellas. No incluir Swagger si no existe ninguna dependencia o configuración que lo habilite.

## Formato de salida

Cuando el puerto se haya resuelto desde `Gloval_Cloud.json` o se haya recibido como fallback, la respuesta final debe contener únicamente dos bloques, titulados exactamente `Endpoints Swagger` y `Endpoints REST`, sin introducción, conclusiones, explicaciones, advertencias, nombres de archivos ni operaciones realizadas. El bloque `Endpoints Swagger` debe aparecer primero y contener las URLs de Swagger detectadas. El bloque `Endpoints REST` debe contener las rutas de controllers y routers descubiertas. Usar una línea por endpoint con este formato:

```text
- <MÉTODO> <URL> — parámetros: <parámetros de ruta, query, headers, cuerpo o ninguno>
```

Ordenar las líneas por prioridad de método: primero todos los `GET`, después todos los `POST` y finalmente el resto de métodos HTTP. Dentro de cada grupo, ordenar por método y URL. Mantener los placeholders de ruta, por ejemplo `{numeroExpediente}`. Si solo se detecta uno de los dos tipos de endpoints, mantener ambos títulos y escribir `Ninguno` en el bloque vacío. Si no se detecta ningún endpoint de ninguno de los dos tipos, responder únicamente `Ninguno`.
