from cargaxml import cargar_xml
from procesador import SistemaAgricola

def datosYO():
    print("Datos del Alumno")
    print("Nombre: Darren Daniel Isaac Castro Espinoza")
    print("Carnet: 202401819")
    print("Curso: Introducción a la progamación y computación 2")
    print("Carrera: Ingeniería en Ciencias y Sistemas")
    print("Semestre: 4to semestre (Segundo semestre 2025)")
    print("Enlace de documentación: https://github.com/DarrenD-07/IPC2_Proyecto1_202401819")

def main():
    sistema = SistemaAgricola()

    while True:
        print("--- MENÚ PRINCIPAL ---")
        print("1. Cargar archivo XML")
        print("2. Procesar información")
        print("3. Generar archivo de salida")
        print("4. Datos del Estudiante")
        print("5. Generar Gráfica")
        print("6. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ruta = input("Ingrese Nombre del archivo XML de entrada: ").strip()
            campos = cargar_xml(ruta)
            if campos is not None:
                sistema.campos.clear()
                for campo in campos:
                    sistema.campos.append(campo)
        elif opcion == "2":
            sistema.procesar()
        elif opcion == "3":
            nombre = input("Ingrese el nombre del archivo de salida: ").strip()
            if not nombre:
                print("Debe ingresar un nombre válido.")
                continue
            try:
                sistema.escribir_salida(nombre)
            except Exception as e:
                print(f"Error al escribir archivo de salida: {e}")
        elif opcion == "4":
            datosYO()
        elif opcion =="5":
            sistema.Graficar()
        elif opcion == "6":
            print("Saliendo")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
