from abc import ABC, abstractmethod

class MultimediaWorkerPort(ABC):
    """
    Puerto para trabajadores multimedia (Generación de Imagen, Video, Audio).
    Sprint 3.5: Definición de estructura.
    """
    @abstractmethod
    def generate_content(self, prompt: str, content_type: str) -> str:
        """
        Genera contenido multimedia.
        :param prompt: Instrucción para la generación.
        :param content_type: 'image', 'video', 'audio'.
        :return: URL o path del contenido generado.
        """
        pass

class BaseWorker(MultimediaWorkerPort):
    def generate_content(self, prompt: str, content_type: str) -> str:
        raise NotImplementedError("Este worker debe implementar generate_content")
