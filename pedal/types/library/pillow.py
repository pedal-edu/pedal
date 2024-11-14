from pedal.types.new_types import ModuleType, FunctionType, void_function, ClassType, \
    InstanceType, bool_function, int_function, str_function, register_builtin_module, \
    TupleType, IntType, StrType, BoolType, DictType, LiteralInt, LiteralStr, \
    FloatType, ListType

_VOID_FUNCTIONS = []
_IMAGE_FUNCTIONS = ['Image']
_IMAGE_STATIC_METHODS = [# From existing
                         'open', 'new', 'fromarray', 'frombytes', 'frombuffer',
                         # Make from scratch
                         'effect_mandelbrot', 'effect_noise', 'linear_gradient',
                         'radial_gradient',
                         # Function versions of methods
                         'alpha_composite', 'blend', 'composite', 'eval',
                         'merge', 'getchannel'
                         ]
_IMAGE_IMAGE_METHODS = ['apply_transparency', 'convert', 'copy',
                        'crop', 'effect_spread', 'filter', 'point',
                        'quantize', 'reduce', 'remap_palette', 'resize',
                        'rotate', 'transform', 'transpose',]
_IMAGE_VOID_METHODS = ['alpha_composite', 'apply_transparency',
                       'frombytes', 'paste', 'putalpha', 'putdata',
                       'putpalette', 'putpixel','save', 'seek', 'show',
                       'thumbnail', 'verify', 'load', 'close']
# TODO: draft, tobytes, tobitmap


def build_pillow_module():

    def _Image_constructor():
        return InstanceType(_Image)

    _ImagePalette = ClassType('ImagePalette', {}, [])
    _Exif = ClassType('Exif', {}, [])
    _ImagePointHandler = ClassType('ImagePointHandler', {}, [])
    _ImagePointTransform = ClassType('ImagePointTransform', {}, [])
    _ImageTransformHandler = ClassType('ImageTransformHandler', {}, [])
    _Transpose = ClassType('Transpose', {
        "FLIP_LEFT_RIGHT": LiteralInt(0),
        "FLIP_TOP_BOTTOM": LiteralInt(1),
        "ROTATE_90": LiteralInt(2),
        "ROTATE_180": LiteralInt(3),
        "ROTATE_270": LiteralInt(4),
        "TRANSPOSE": LiteralInt(5),
        "TRANSVERSE": LiteralInt(6),
    }, [])
    _Transform = ClassType("Transform", {
        "AFFINE": LiteralStr("AFFINE"),
        "EXTENT": LiteralStr("EXTENT"),
        "QUAD": LiteralStr("QUAD"),
        "MESH": LiteralStr("MESH"),
        "PERSPECTIVE": LiteralStr("PERSPECTIVE"),
    }, [])
    _Resample = ClassType("Resample", {
        "NEAREST": LiteralInt(0),
        "BOX": LiteralInt(4),
        "BILINEAR": LiteralInt(2),
        "HAMMING": LiteralInt(5),
        "BICUBIC": LiteralInt(3),
        "LANCZOS": LiteralInt(1),
    }, [])
    _Dither = ClassType("Dither", {
        "NONE": LiteralInt(0),
        "FLOYDSTEINBERG": LiteralInt(1),
        "ORDERED": LiteralInt(2),
        "RASTERIZE": LiteralInt(3),
    }, [])
    _Palette = ClassType("Palette", {
        "WEB": LiteralInt(0),
        "ADAPTIVE": LiteralInt(1),
    }, [])
    _Quantize = ClassType("Quantize", {
        "MEDIANCUT": LiteralInt(0),
        "MAXCOVERAGE": LiteralInt(1),
        "FASTOCTREE": LiteralInt(2),
        "LIBIMAGEQUANT": LiteralInt(3),
    }, [])

    _CLASS_FIELDS: dict = {
        # Fields
        'size': TupleType([IntType(), IntType()]),
        'width': IntType(),
        'height': IntType(),
        'mode': StrType(),
        'format': StrType(),
        'filename': StrType(),
        'palette': InstanceType(_ImagePalette),
        'info': DictType(),
        'is_animated': BoolType(),
        'n_frames': IntType(),
        'has_transparency_data': BoolType(),
        # Weird methods
        # TODO: How do you specify a tuple of unknown number of integers?
        'entropy': FunctionType('entropy', returns=FloatType),
        'getbands': FunctionType('getbands', returns=lambda: TupleType([StrType()])),
        'getbbox': FunctionType('getbbox', returns=lambda: TupleType([IntType(), IntType(), IntType(), IntType()])),
        'getcolors': FunctionType('getcolors', returns=lambda: ListType(element_type=TupleType([IntType(), FloatType()]))),
        'getexif': FunctionType('getexif', returns=lambda: InstanceType(_Exif)),
        'getpalette': FunctionType('getpalette', returns=lambda: ListType(element_type=IntType())),
        'getextrema': FunctionType('getextrema', returns=lambda: TupleType([FloatType(), FloatType()])),
        'getpixel': FunctionType('getpixel', returns=lambda: ListType(element_type=IntType())),
        'tell': FunctionType('tell', returns=lambda: IntType()),

    }
    _Image = ClassType('Image', _CLASS_FIELDS, [])
    _CLASS_FIELDS.update({
        name: FunctionType(name, returns=_Image_constructor)
        for name in _IMAGE_IMAGE_METHODS
    })
    _CLASS_FIELDS.update({
        name: void_function(name)
        for name in _IMAGE_VOID_METHODS
    })


    _IMAGE_MODULE_FUNCTIONS: dict = {
        'Image': _Image,
        'ImagePalette': _ImagePalette,
        'Exif': _Exif,
        'ImagePointHandler': _ImagePointHandler,
        'ImagePointTransform': _ImagePointTransform,
        'ImageTransformHandler': _ImageTransformHandler,
        'Transpose': _Transpose,
        'Transform': _Transform,
        'Resample': _Resample,
        'Dither': _Dither,
        'Palette': _Palette,
        'Quantize': _Quantize,
    }
    _IMAGE_MODULE = ModuleType('Image', fields=_IMAGE_MODULE_FUNCTIONS)
    _IMAGE_MODULE_FUNCTIONS.update({
        name: FunctionType(name, returns=_Image_constructor)
        for name in _IMAGE_STATIC_METHODS
    })

    return ModuleType('PIL', {}, {'Image': _IMAGE_MODULE})


register_builtin_module('PIL', build_pillow_module)
