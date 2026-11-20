"""Быстрый рендер Blender на процессоре (контейнер без видеокарты, 4 ядра). Владелец 20.11: «все настройки ускорения
применять всегда».

Использование внутри сцены Blender:  import blender_fast; blender_fast.apply(bpy.context.scene)
или из командной строки:  blender -b scene.blend --python scripts/blender_fast.py -a

Что делает и почему (каждое — ускорение без заметной потери картинки рисованного 3D-ситкома):
- Cycles на CPU, все потоки (threads_mode AUTO) — других рендеров параллельно не запускать;
- 48 сэмплов + адаптивные сэмплы (порог 0.03): чистые участки не досчитываются;
- шумодав OpenImageDenoise на CPU: убирает зерно от малого числа сэмплов;
- меньше отскоков света (4 всего, диффуз 2, глянец 2), каустика выключена;
- persistent data: сцена не пересобирается между кадрами анимации;
- 720×1280 (как у референса), увеличение до 1080×1920 — потом ffmpeg (lanczos), пикселей в 2,25 раза меньше;
- упрощение (simplify): ограничение подразделения и размера текстур;
- один большой тайл (auto tile 2048) — на CPU быстрее мелких.
"""

FAST = dict(samples=48, adaptive_threshold=0.03, max_bounces=4, diffuse=2, glossy=2, transmission=4, volume=0,
            res=(720, 1280), tile=2048, simplify_subdiv=2, texture_limit="2048")


def apply(scene, **over):
    c = {**FAST, **over}
    scene.render.engine = "CYCLES"
    cy = scene.cycles
    cy.device = "CPU"
    scene.render.threads_mode = "AUTO"
    cy.samples = c["samples"]
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = c["adaptive_threshold"]
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    cy.max_bounces = c["max_bounces"]
    cy.diffuse_bounces = c["diffuse"]
    cy.glossy_bounces = c["glossy"]
    cy.transmission_bounces = c["transmission"]
    cy.volume_bounces = c["volume"]
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.blur_glossy = 1.0
    cy.use_auto_tile = True
    cy.tile_size = c["tile"]
    scene.render.use_persistent_data = True
    scene.render.resolution_x, scene.render.resolution_y = c["res"]
    scene.render.resolution_percentage = 100
    scene.render.use_simplify = True
    scene.render.simplify_subdivision_render = c["simplify_subdiv"]
    cy.texture_limit_render = c["texture_limit"]
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 93
    return scene


UPSCALE = "ffmpeg -framerate 30 -i frames/%04d.jpg -vf scale=1080:1920:flags=lanczos -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4"

if __name__ == "__main__":
    try:
        import bpy
        apply(bpy.context.scene)
        print("blender_fast: настройки применены", FAST)
    except ImportError:
        print(__doc__)
