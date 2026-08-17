---
name: gloval-java-legacy-standards
description: Estándares de codificación Java en Gloval (literales, nomenclatura, try-with-resources, indentación, encapsulación, inmutabilidad, Lombok, logging MessageFormat, paquetes, XSD interno, anti-verbosidad, comentarios, BBDD Postgres), manejo de archivos legacy en ISO-8859-1/Windows-1252 y entorno SDKMAN Java 8. Invocar al editar/crear cualquier archivo `.java`, al revisar código Java de Gloval, al diseñar tablas Postgres del proyecto, o al hablar de "estándares Java Gloval", "encoding legacy", "Java 8 Gloval", "sdk use java".
---

# gloval-java-legacy-standards

Aplica a todo código Java en proyectos Gloval. Cumplir SIEMPRE salvo justificación explícita.

---

## 1. Literales y Constantes

No debe haber literales de string/números en el código excepto constantes.

- **Dónde van las constantes:** siempre en `helpers.ConstantsHelper`, agrupadas en clases internas estáticas por temática.
- Consumirlas siempre con prefijo de clase interna e `import static`: `import static helpers.ConstantsHelper.Propiedad;` y uso `Propiedad.RUTA_PROPERTIES`.
- Nunca declarar `private static final String X = "..."` dentro del servlet o clase de lógica.
- Ejemplo:
  ```java
  // helpers/ConstantsHelper.java
  public class ConstantsHelper {
      public static class BaseDatos {
          public static final String OCO = "oco";
      }
  }

  // uso
  import static helpers.ConstantsHelper.BaseDatos;
  if (BaseDatos.OCO.equals(baseDatos)) { ... }
  ```
- **Catálogos Gloval** (`tipoinm`, `tipovia`, etc.): consultar el nombre canónico en `/home/abraham/git/libconstants` (`es.gloval.librerias.libconstants.ConstantsHelper`). Los proyectos Java 8 no pueden depender de ella por su bytecode moderno: duplicar en el `ConstantsHelper` local solo las constantes necesarias, conservando los nombres canónicos.
- **Catálogos de cliente:** usar prefijo `Su*` (`SuTipoVia`); para catálogos Gloval, no usar prefijo (`TipoVia`).

### Mappers de catálogos

- Nombrar y ubicar el mapper por lo que devuelve; tomar como referencia Abanca `conversion/origen*/`.
  - `SuTipoViaMapper.map(tipoVia)` devuelve un código del catálogo del cliente.
  - `TipoViaMapper.map(suTipoVia)` devuelve un código del catálogo Gloval.
- Cada código válido del catálogo de entrada debe tener un mapeo explícito o caer deliberadamente en un valor por defecto documentado. No añadir constantes de catálogo sin comprobar su tratamiento en el mapper.
- Al modificar equivalencias, actualizar las pruebas que cubren los códigos afectados y los casos nulo, vacío, desconocido y por defecto.

## 2. Nomenclatura de Variables y Constantes

- Variables: nombres específicos e intuitivos, sin abreviaciones.
  - ❌ `vtastotal`, `conexion`, `cod_advert`
  - ✅ `valorTasacionTotal`, `conexionValtecnic2`, `CODIGO_ADVERTENCIA`
- Los nombres compuestos deben conservar los límites de palabra en camelCase: `tipoVia`, no `tipovia`.
- Constantes: especificar el contexto completo.

## 3. Try-with-Resources

Todo recurso `AutoCloseable` debe usar try-with-resources (Connection, ResultSet, BufferedReader, etc.).

```java
try (Connection conexionValtecnic2 = Utilidades.Conexion.getPoolConnection(...)) {
    validar(conexionValtecnic2);
} catch (Exception e) {
    log.error(...);
}
```

## 4. Indentación

- 2 espacios por nivel.
- Braces `{}` SIEMPRE, incluso en sentencias de una línea.
- Reformatear con Ctrl+Alt+L en IntelliJ.
- Evitar one-liners anidados complejos.

## 5. Encapsulación

Extraer validaciones y funcionalidades complejas a métodos separados.

## 6. Programación Inmutable

- Variables locales y campos siempre `final` cuando no deban reasignarse. No usar `var`: el entorno objetivo es Java 8 y esa sintaxis se introdujo en Java 10.
- Parámetros de método siempre `final`: `void procesar(final String numexp, final Connection conexionValtecnic2)`.
- Parámetros de `catch` siempre `final`: `catch (final IOException e)`.
- Aplicar estas reglas también cuando el código legacy circundante no las siga: todo código nuevo o modificado debe cumplirlas.
- Uso obligatorio: Streams, Optional.
- Evitar mutación de estado.

### Clases utilitarias

- Toda clase que solo contenga miembros estáticos y no tenga estado de instancia debe declararse `final` y tener constructor privado.
- Usar Lombok con el tipo de acceso explícito: `@NoArgsConstructor(access = AccessLevel.PRIVATE)`; no usar el import estático de `PRIVATE`.
- No aplicar este patrón a clases que deban instanciarse, heredarse o gestionarse mediante inyección de dependencias.

```java
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class TipoViaMapper {

  public static String map(final String tipoVia) {
    // ...
  }
}
```

## 7. Crear Objetos

- EVITAR `new` siempre que sea posible.
- Alternativa: Lombok `@Builder`.

## 8. Logging

Patrón obligatorio:

```java
import static java.text.MessageFormat.format;

log.info(format("Generando informacion de la finca [{0}] para el expediente [{1}]",
         finca, numeroExpediente));

log.error(format("Error generando finca [{0}] para expediente [{1}]. Causa: [{2}]",
         finca, expediente, e.getMessage()), e);
```

Reglas:
- Usar `[]` para resaltar información específica.
- Logger se llama `log`.
- En errores: incluir `e.getMessage()` Y pasar la `Exception` como último arg.
- Para números: `{0,number,#}` en MessageFormat.

## 9. Rutas de Archivos y URLs

- Archivos: `Paths.get()`.
- URLs: `URI.create().resolve()`.

## 10. Convenciones de Paquetes

- Interfaces de clientes: `es.gloval.clientes.{cliente}.*` (ej. `es.gloval.clientes.sabadell.*`).
- Aplicaciones: `es.gloval.aplicaciones.{nombre}.*`.
- Servicios: `es.gloval.servicios.{nombre}.*`.
- Todos en minúsculas.

## 11. XSD Siempre Interno

Los XSD usados como esquema de comunicación con cliente deben estar en el source code, nunca apuntar a archivos externos del servidor.

## 12. Evitar Verbosidad

- No usar FQN:
  - ❌ `java.sql.ResultSet resultset`
  - ✅ `ResultSet resultSet`
- Constantes con prefijo de clase interna: convención enforzada por el hook `~/.claude/hooks/java-constants-prefix.sh`.
  - Correcto: `import static helpers.ConstantsHelper.TipoInmueble;` y uso `TipoInmueble.SOLAR`.
  - Bloqueado: `import static` de constante suelta, type import plano de la clase, type import no-static de clase interna.
- Los métodos estáticos de clases `*Helper` deben importarse estáticamente y llamarse sin prefijo de clase:
  ```java
  import static helpers.StringHelper.isNullOrBlank;

  if (isNullOrBlank(tipoVia)) { ... }
  ```
- Esta regla no cambia el acceso a constantes: se importa estáticamente la clase interna y se conserva el prefijo, por ejemplo `TipoVia.CALLE`.

## 13. Comentarios

- Solo comentarios que aporten valor.
- Nombres descriptivos: variables, métodos y constantes autodocumentados.
- Eliminar comentarios obvios que repitan el código.
- **Sin acentos en comentarios** (proyectos legacy en encoding ISO-8859-1):
  - ❌ `Obtén el número de expediente`
  - ✅ `Obtene el numero de expediente`

## 14. Base de Datos (Postgres)

- Schema obligatorio: `CREATE TABLE public.tabla_name`.
- Nomenclatura: snake_case, minúsculas.
- Evitar prefijos redundantes; no repetir contexto obvio.
- Comentarios obligatorios en tablas y cada columna explicando propósito y formato.
- Claves primarias compuestas si es necesario (depender de entidad principal).
- Campos estándar: `fecha_creacion`, `usuario_creacion`, `fecha_modificacion`, `usuario_modificacion`.
- Evitar tildes, caracteres especiales, ñ.

---

## Encoding Java legacy (ISO-8859-1 / Windows-1252)

- Hook `~/.claude/hooks/java-encoding-guard.sh` bloquea Edit/Write/MultiEdit en `.java` cuando el archivo está en `iso-8859-1` / `windows-1252` (proyectos legacy con esos encodings declarados en `build.gradle`).
- Para esos archivos usar:
  - `sed -i` (sustitución byte-a-byte), o
  - `python3` en modo binario.
- Clases de constantes (`*Constants*.java`, `Constantes*.java`) se mantienen en ISO-8859-1; las clases normales en UTF-8 sin string literals con acentos (mover a la clase de constantes).
- Cuando un valor funcional necesite caracteres no ASCII, representarlos con escapes Unicode independientemente del encoding del fichero:
  ```java
  public static final String CAMINO = "C\u00BA";
  public static final String CARRETERA = "C\u00AA";
  public static final String PASEO = "P\u00BA.";
  ```
- No escribir esos caracteres directamente ni usar escapes octales como `\272`. No sustituirlos por aproximaciones ASCII si cambia el valor enviado o almacenado.

---

## Entorno Java

Antes de compilar/test en proyectos legacy (Gradle antiguo, sin módulos, source/target 1.8, `javax.*` imports):

```bash
sdk use java 8.0.432-tem
```

Compilar siempre con `clean` previo; una build incremental sucia puede producir falsos `cannot find symbol`:

```bash
./gradlew clean compileJava
```
