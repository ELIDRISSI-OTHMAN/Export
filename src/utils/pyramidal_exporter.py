"""
Pyramidal TIFF exporter with proper transformation support
"""

import os
import numpy as np
from typing import List, Dict, Tuple, Optional, Callable
import logging
import tempfile
import shutil
import math

# Import QApplication for processEvents
from PyQt6.QtWidgets import QApplication

try:
    import openslide
    OPENSLIDE_AVAILABLE = True
except ImportError:
    OPENSLIDE_AVAILABLE = False

try:
    import tifffile
    TIFFFILE_AVAILABLE = True
except ImportError:
    TIFFFILE_AVAILABLE = False

try:
    import pyvips
    PYVIPS_AVAILABLE = True
    # Enable pyvips cache for better performance
    pyvips.cache_set_max(100)
    pyvips.cache_set_max_mem(100 * 1024 * 1024)  # 100MB
except ImportError:
    PYVIPS_AVAILABLE = False

from ..core.fragment import Fragment

class PyramidalExporter:
    """Handles export of stitched pyramidal TIFF files with proper transformation support"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Check available libraries and recommend best approach
        if PYVIPS_AVAILABLE:
            self.logger.info("Using pyvips for pyramidal TIFF export (recommended)")
            self.export_method = "pyvips"
        elif TIFFFILE_AVAILABLE:
            self.logger.info("Using tifffile for pyramidal TIFF export (fallback)")
            self.export_method = "tifffile"
        else:
            self.logger.error("No suitable library available for pyramidal TIFF export")
            self.export_method = None
            
    def export_pyramidal_tiff(self, fragments: List[Fragment], output_path: str,
                             selected_levels: List[int], compression: str = "LZW",
                             tile_size: int = 256, progress_callback: Optional[Callable] = None) -> bool:
        """
        Export fragments as a stitched pyramidal TIFF with proper transformation support
        
        Args:
            fragments: List of visible Fragment objects
            output_path: Output file path
            selected_levels: List of pyramid levels to export
            compression: Compression method ("LZW", "JPEG", "Deflate", "None")
            tile_size: Tile size for pyramid (default 256)
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            self.logger.info(f"Starting pyramidal TIFF export to {output_path}")
            
            # Filter visible fragments with source files
            visible_fragments = [f for f in fragments if f.visible and f.file_path and os.path.exists(f.file_path)]
            if not visible_fragments:
                raise ValueError("No visible fragments with valid source files to export")
            
            # Validate selected levels
            if not selected_levels:
                raise ValueError("No pyramid levels selected for export")
                
            # Choose export method based on available libraries
            if self.export_method == "pyvips" and PYVIPS_AVAILABLE:
                return self._export_with_pyvips(
                    visible_fragments, output_path, selected_levels,
                    compression, tile_size, progress_callback
                )
            elif self.export_method == "tifffile" and TIFFFILE_AVAILABLE:
                return self._export_with_tifffile_corrected(
                    visible_fragments, output_path, selected_levels,
                    compression, progress_callback
                )
            else:
                raise RuntimeError("No suitable export method available")
                
        except Exception as e:
            self.logger.error(f"Pyramidal TIFF export failed: {str(e)}")
            if progress_callback:
                progress_callback(0, f"Export failed: {str(e)}")
            return False
    
    def _export_with_pyvips(self, fragments: List[Fragment], output_path: str,
                           selected_levels: List[int], compression: str, tile_size: int,
                           progress_callback: Optional[Callable]) -> bool:
        """Export using pyvips (recommended method for true pyramidal TIFFs)"""
        try:
            if progress_callback:
                progress_callback(5, "Initializing pyvips export...")
                QApplication.processEvents()
            
            # Calculate composite bounds at level 0 (highest resolution)
            level_0_bounds = self._calculate_composite_bounds_at_level(fragments, 0)
            if not level_0_bounds:
                raise ValueError("Could not calculate composite bounds")
            
            min_x, min_y, max_x, max_y = level_0_bounds
            base_width = int(max_x - min_x)
            base_height = int(max_y - min_y)
            
            self.logger.info(f"Base composite size: {base_width} x {base_height}")
            
            # Create base level composite using pyvips
            if progress_callback:
                progress_callback(10, "Creating base level composite...")
                QApplication.processEvents()
            
            base_composite = self._create_pyvips_composite(fragments, 0, level_0_bounds)
            if base_composite is None:
                raise ValueError("Failed to create base composite")
            
            # Configure compression for pyvips
            save_options = self._get_pyvips_save_options(compression, tile_size)
            
            # Create pyramid levels
            if len(selected_levels) == 1 and selected_levels[0] == 0:
                # Single level export
                if progress_callback:
                    progress_callback(90, "Saving single level TIFF...")
                    QApplication.processEvents()
                
                base_composite.write_to_file(output_path, **save_options)
            else:
                # Multi-level pyramid export
                if progress_callback:
                    progress_callback(50, "Creating pyramid levels...")
                    QApplication.processEvents()
                
                # Create pyramid using pyvips
                pyramid_options = {
                    'tile': True,
                    'tile_width': tile_size,
                    'tile_height': tile_size,
                    'pyramid': True,
                    'bigtiff': True,  # Use BigTIFF for large files
                    **save_options
                }
                
                # Remove conflicting options
                pyramid_options.pop('tile', None)  # Remove the boolean tile option
                
                if progress_callback:
                    progress_callback(90, "Saving pyramidal TIFF...")
                    QApplication.processEvents()
                
                base_composite.tiffsave(output_path, **pyramid_options)
            
            if progress_callback:
                progress_callback(100, "Export complete")
                QApplication.processEvents()
                
            self.logger.info("Pyramidal TIFF export completed successfully with pyvips")
            return True
            
        except Exception as e:
            self.logger.error(f"pyvips export failed: {str(e)}")
            if progress_callback:
                progress_callback(0, f"pyvips export failed: {str(e)}")
            return False
    
    def _create_pyvips_composite(self, fragments: List[Fragment], level: int, 
                                bounds: Tuple[float, float, float, float]) -> Optional['pyvips.Image']:
        """Create composite image using pyvips for better memory management"""
        try:
            min_x, min_y, max_x, max_y = bounds
            downsample = 2 ** level
            
            # Calculate dimensions at this level
            width = int((max_x - min_x) / downsample)
            height = int((max_y - min_y) / downsample)
            
            if width <= 0 or height <= 0:
                return None
            
            # Create blank canvas
            canvas = pyvips.Image.black(width, height, bands=4)  # RGBA
            
            # Composite each fragment
            for fragment in fragments:
                try:
                    # Load and transform fragment at the specified level
                    fragment_image = self._load_fragment_pyvips(fragment, level)
                    if fragment_image is None:
                        continue
                    
                    # Calculate position in composite
                    scaled_x = int((fragment.x - min_x) / downsample)
                    scaled_y = int((fragment.y - min_y) / downsample)
                    
                    # Ensure fragment has alpha channel
                    if fragment_image.bands == 3:
                        alpha = pyvips.Image.black(fragment_image.width, fragment_image.height) + 255
                        fragment_image = fragment_image.bandjoin(alpha)
                    
                    # Apply opacity
                    if fragment.opacity < 1.0:
                        alpha_band = fragment_image.extract_band(3) * fragment.opacity
                        rgb_bands = fragment_image.extract_band(0, n=3)
                        fragment_image = rgb_bands.bandjoin(alpha_band)
                    
                    # Composite onto canvas
                    canvas = canvas.composite2(fragment_image, 'over', x=scaled_x, y=scaled_y)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to composite fragment {fragment.name}: {e}")
                    continue
            
            return canvas
            
        except Exception as e:
            self.logger.error(f"Failed to create pyvips composite: {str(e)}")
            return None
    
    def _load_fragment_pyvips(self, fragment: Fragment, level: int) -> Optional['pyvips.Image']:
        """Load fragment at specific level using pyvips with transformations"""
        try:
            # Load image at specified level
            if fragment.file_path.lower().endswith(('.tif', '.tiff')):
                # For TIFF files, try to load specific level
                try:
                    image = pyvips.Image.new_from_file(fragment.file_path, page=level)
                except:
                    # Fallback to level 0 and downsample
                    image = pyvips.Image.new_from_file(fragment.file_path, page=0)
                    if level > 0:
                        scale = 1.0 / (2 ** level)
                        image = image.resize(scale)
            else:
                # For other formats, load and downsample if needed
                image = pyvips.Image.new_from_file(fragment.file_path)
                if level > 0:
                    scale = 1.0 / (2 ** level)
                    image = image.resize(scale)
            
            # Apply transformations
            image = self._apply_pyvips_transforms(image, fragment)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to load fragment {fragment.name} with pyvips: {e}")
            return None
    
    def _apply_pyvips_transforms(self, image: 'pyvips.Image', fragment: Fragment) -> 'pyvips.Image':
        """Apply transformations to pyvips image"""
        try:
            result = image
            
            # Apply horizontal flip
            if fragment.flip_horizontal:
                result = result.fliphor()
            
            # Apply vertical flip
            if fragment.flip_vertical:
                result = result.flipver()
            
            # Apply rotation
            if abs(fragment.rotation) > 0.01:
                # pyvips rotate expects angle in degrees
                result = result.rotate(fragment.rotation, background=[0, 0, 0, 0])
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to apply pyvips transforms: {e}")
            return image
    
    def _get_pyvips_save_options(self, compression: str, tile_size: int) -> Dict:
        """Get pyvips save options for different compression types"""
        options = {
            'tile_width': tile_size,
            'tile_height': tile_size,
        }
        
        compression_map = {
            "LZW": "lzw",
            "JPEG": "jpeg", 
            "Deflate": "deflate",
            "None": "none"
        }
        
        pyvips_compression = compression_map.get(compression, "lzw")
        options['compression'] = pyvips_compression
        
        # JPEG-specific options
        if pyvips_compression == "jpeg":
            options['Q'] = 95  # JPEG quality
            options['rgbjpeg'] = True  # Force RGB JPEG
        
        return options
    
    def _export_with_tifffile_corrected(self, fragments: List[Fragment], output_path: str,
                                       selected_levels: List[int], compression: str,
                                       progress_callback: Optional[Callable]) -> bool:
        """Corrected tifffile export method with proper transformation handling"""
        try:
            if not TIFFFILE_AVAILABLE:
                raise ImportError("tifffile required for export")
            
            # Process each level with correct transformation application
            level_images = {}
            total_levels = len(selected_levels)
            
            for i, level in enumerate(selected_levels):
                if progress_callback:
                    progress = int(10 + (i / total_levels) * 70)
                    progress_callback(progress, f"Processing level {level}")
                    QApplication.processEvents()
                
                try:
                    # Calculate bounds for this specific level
                    bounds = self._calculate_composite_bounds_at_level_corrected(fragments, level)
                    if not bounds:
                        self.logger.warning(f"Could not calculate bounds for level {level}")
                        continue
                    
                    # Render composite with proper transformation scaling
                    composite = self._render_composite_at_level_corrected(fragments, level, bounds)
                    if composite is not None:
                        level_images[level] = composite
                        self.logger.info(f"Successfully processed level {level}, size: {composite.shape}")
                    else:
                        self.logger.warning(f"Failed to render composite for level {level}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing level {level}: {str(e)}")
                    continue
            
            if not level_images:
                raise ValueError("No levels could be processed successfully")
            
            # Save as proper pyramidal TIFF
            if progress_callback:
                progress_callback(85, "Saving pyramidal TIFF...")
                QApplication.processEvents()
            
            success = self._save_pyramidal_tiff(level_images, output_path, compression, selected_levels)
            
            if progress_callback:
                progress_callback(100, "Export complete")
                QApplication.processEvents()
                
            return success
            
        except Exception as e:
            self.logger.error(f"Corrected tifffile export failed: {str(e)}")
            if progress_callback:
                progress_callback(0, f"Export failed: {str(e)}")
            return False
    
    def _calculate_composite_bounds_at_level_corrected(self, fragments: List[Fragment], level: int) -> Optional[Tuple[float, float, float, float]]:
        """Calculate composite bounds with proper level scaling"""
        if not fragments:
            return None
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        downsample = 2 ** level
        
        for fragment in fragments:
            try:
                # Get original image dimensions at the target level
                original_dims = self._get_image_dimensions_at_level(fragment.file_path, level)
                if not original_dims:
                    continue
                
                orig_width, orig_height = original_dims
                
                # Apply transformations to get final dimensions
                final_dims = self._calculate_transformed_dimensions(
                    orig_width, orig_height, fragment.rotation
                )
                final_width, final_height = final_dims
                
                # Fragment positions are at level 0 scale, scale them for this level
                scaled_x = fragment.x / downsample
                scaled_y = fragment.y / downsample
                
                min_x = min(min_x, scaled_x)
                min_y = min(min_y, scaled_y)
                max_x = max(max_x, scaled_x + final_width)
                max_y = max(max_y, scaled_y + final_height)
                
            except Exception as e:
                self.logger.warning(f"Could not get bounds for fragment {fragment.name} at level {level}: {e}")
                continue
        
        if min_x == float('inf'):
            return None
        
        return (min_x, min_y, max_x, max_y)
    
    def _get_image_dimensions_at_level(self, file_path: str, level: int) -> Optional[Tuple[int, int]]:
        """Get image dimensions at specific pyramid level"""
        try:
            from ..core.image_loader import ImageLoader
            loader = ImageLoader()
            
            # Get pyramid info
            pyramid_info = loader.get_pyramid_info(file_path)
            if level < len(pyramid_info['level_dimensions']):
                return pyramid_info['level_dimensions'][level]
            else:
                # Fallback: calculate from level 0
                if pyramid_info['level_dimensions']:
                    base_width, base_height = pyramid_info['level_dimensions'][0]
                    downsample = 2 ** level
                    return (int(base_width / downsample), int(base_height / downsample))
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get dimensions for {file_path} at level {level}: {e}")
            return None
    
    def _calculate_transformed_dimensions(self, width: int, height: int, rotation: float) -> Tuple[int, int]:
        """Calculate dimensions after rotation transformation"""
        if abs(rotation) < 0.01:
            return (width, height)
        
        # Calculate rotated bounding box
        angle_rad = math.radians(rotation)
        cos_a = abs(math.cos(angle_rad))
        sin_a = abs(math.sin(angle_rad))
        
        new_width = int(width * cos_a + height * sin_a)
        new_height = int(width * sin_a + height * cos_a)
        
        return (new_width, new_height)
    
    def _render_composite_at_level_corrected(self, fragments: List[Fragment], level: int,
                                           bounds: Tuple[float, float, float, float]) -> Optional[np.ndarray]:
        """Render composite with corrected transformation handling"""
        try:
            min_x, min_y, max_x, max_y = bounds
            width = int(max_x - min_x)
            height = int(max_y - min_y)
            
            if width <= 0 or height <= 0:
                return None
            
            # Create composite array
            composite = np.zeros((height, width, 4), dtype=np.uint8)
            downsample = 2 ** level
            
            for fragment in fragments:
                try:
                    # Load fragment at correct level with transformations
                    fragment_image = self._load_and_transform_fragment_corrected(fragment, level)
                    if fragment_image is None:
                        continue
                    
                    # Calculate position in composite (scale fragment position to this level)
                    scaled_x = int((fragment.x / downsample) - min_x)
                    scaled_y = int((fragment.y / downsample) - min_y)
                    
                    # Composite the fragment
                    self._composite_fragment_corrected(composite, fragment_image, scaled_x, scaled_y, fragment.opacity)
                    
                except Exception as e:
                    self.logger.error(f"Error compositing fragment {fragment.name}: {e}")
                    continue
            
            return composite
            
        except Exception as e:
            self.logger.error(f"Failed to render composite at level {level}: {str(e)}")
            return None
    
    def _load_and_transform_fragment_corrected(self, fragment: Fragment, level: int) -> Optional[np.ndarray]:
        """Load fragment at specific level and apply transformations correctly"""
        try:
            from ..core.image_loader import ImageLoader
            loader = ImageLoader()
            
            # Load original image at the specified pyramid level
            original_image = loader.load_image(fragment.file_path, level)
            if original_image is None:
                return None
            
            # Apply transformations in correct order
            transformed_image = original_image.copy()
            
            # Apply flips first (these don't change dimensions)
            if fragment.flip_horizontal:
                transformed_image = np.fliplr(transformed_image)
            
            if fragment.flip_vertical:
                transformed_image = np.flipud(transformed_image)
            
            # Apply rotation last (this changes dimensions)
            if abs(fragment.rotation) > 0.01:
                transformed_image = self._rotate_image_opencv(transformed_image, fragment.rotation)
            
            return transformed_image
            
        except Exception as e:
            self.logger.error(f"Failed to load and transform fragment {fragment.name}: {e}")
            return None
    
    def _rotate_image_opencv(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image using OpenCV with proper handling of dimensions"""
        import cv2
        
        if abs(angle) < 0.01:
            return image
        
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        # Get rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new bounding box
        cos_val = abs(rotation_matrix[0, 0])
        sin_val = abs(rotation_matrix[0, 1])
        new_width = int((height * sin_val) + (width * cos_val))
        new_height = int((height * cos_val) + (width * sin_val))
        
        # Adjust rotation matrix for new center
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]
        
        # Apply rotation with proper border handling
        if len(image.shape) == 3 and image.shape[2] == 4:
            # RGBA image
            rotated = cv2.warpAffine(
                image, rotation_matrix, (new_width, new_height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0)
            )
        else:
            # RGB image
            rotated = cv2.warpAffine(
                image, rotation_matrix, (new_width, new_height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0)
            )
        
        return rotated
    
    def _composite_fragment_corrected(self, composite: np.ndarray, fragment_image: np.ndarray,
                                    x: int, y: int, opacity: float):
        """Composite fragment with proper alpha blending"""
        try:
            frag_h, frag_w = fragment_image.shape[:2]
            comp_h, comp_w = composite.shape[:2]
            
            # Calculate intersection
            src_x1 = max(0, -x)
            src_y1 = max(0, -y)
            src_x2 = min(frag_w, comp_w - x)
            src_y2 = min(frag_h, comp_h - y)
            
            dst_x1 = max(0, x)
            dst_y1 = max(0, y)
            dst_x2 = dst_x1 + (src_x2 - src_x1)
            dst_y2 = dst_y1 + (src_y2 - src_y1)
            
            if src_x2 <= src_x1 or src_y2 <= src_y1:
                return
            
            # Extract regions
            frag_region = fragment_image[src_y1:src_y2, src_x1:src_x2]
            
            # Ensure RGBA format
            if frag_region.shape[2] == 3:
                alpha_channel = np.full(frag_region.shape[:2] + (1,), 255, dtype=np.uint8)
                frag_region = np.concatenate([frag_region, alpha_channel], axis=2)
            
            # Apply opacity and alpha blend
            frag_alpha = (frag_region[:, :, 3:4] / 255.0) * opacity
            frag_rgb = frag_region[:, :, :3].astype(np.float32)
            
            comp_region = composite[dst_y1:dst_y2, dst_x1:dst_x2]
            comp_alpha = comp_region[:, :, 3:4] / 255.0
            comp_rgb = comp_region[:, :, :3].astype(np.float32)
            
            # Alpha blending
            out_alpha = frag_alpha + (1 - frag_alpha) * comp_alpha
            
            # Avoid division by zero
            mask = out_alpha[:, :, 0] > 0
            out_rgb = np.zeros_like(frag_rgb)
            
            if np.any(mask):
                out_rgb[mask, :] = (frag_alpha[mask, :] * frag_rgb[mask, :] + 
                                   (1 - frag_alpha[mask, :]) * comp_rgb[mask, :]) / out_alpha[mask, :]
            
            # Update composite
            composite[dst_y1:dst_y2, dst_x1:dst_x2, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
            composite[dst_y1:dst_y2, dst_x1:dst_x2, 3:4] = np.clip(out_alpha * 255, 0, 255).astype(np.uint8)
            
        except Exception as e:
            self.logger.error(f"Failed to composite fragment: {e}")
    
    def _save_pyramidal_tiff(self, level_images: Dict[int, np.ndarray], output_path: str,
                           compression: str, selected_levels: List[int]) -> bool:
        """Save images as a proper pyramidal TIFF structure"""
        try:
            # Configure compression
            compression_map = {
                "LZW": "lzw",
                "JPEG": "jpeg",
                "Deflate": "zlib",
                "None": None
            }
            tiff_compression = compression_map.get(compression)
            
            # Prepare images in pyramid order (level 0 first)
            sorted_levels = sorted(level_images.keys())
            
            if len(sorted_levels) == 1:
                # Single level
                image = level_images[sorted_levels[0]]
                save_kwargs = {
                    'compression': tiff_compression,
                    'photometric': 'rgb',
                    'tile': (256, 256)
                }
                save_kwargs = {k: v for k, v in save_kwargs.items() if v is not None}
                
                tifffile.imwrite(output_path, image, **save_kwargs)
            else:
                # Multi-level pyramid
                with tifffile.TiffWriter(output_path, bigtiff=True) as tiff_writer:
                    for i, level in enumerate(sorted_levels):
                        image = level_images[level]
                        
                        # Convert RGBA to RGB for JPEG compression
                        if tiff_compression == "jpeg" and image.shape[2] == 4:
                            image = self._rgba_to_rgb(image)
                        
                        save_kwargs = {
                            'compression': tiff_compression,
                            'photometric': 'rgb',
                            'tile': (256, 256),
                            'subifds': len(sorted_levels) - 1 if i == 0 else None  # Create subIFDs for pyramid
                        }
                        save_kwargs = {k: v for k, v in save_kwargs.items() if v is not None}
                        
                        tiff_writer.write(image, **save_kwargs)
            
            self.logger.info(f"Saved pyramidal TIFF with {len(sorted_levels)} levels")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save pyramidal TIFF: {e}")
            return False
    
    def _rgba_to_rgb(self, rgba_image: np.ndarray, background_color=(255, 255, 255)) -> np.ndarray:
        """Convert RGBA image to RGB with specified background color"""
        if rgba_image.shape[2] != 4:
            return rgba_image[:, :, :3]
        
        rgb = rgba_image[:, :, :3].astype(np.float32)
        alpha = rgba_image[:, :, 3:4].astype(np.float32) / 255.0
        
        background = np.full_like(rgb, background_color, dtype=np.float32)
        result = (alpha * rgb + (1 - alpha) * background).astype(np.uint8)
        
        return result

    @staticmethod
    def get_recommended_libraries() -> Dict[str, str]:
        """Get recommended libraries for pyramidal TIFF export"""
        return {
            "pyvips": "Recommended - Fast, memory-efficient, true pyramidal TIFF support",
            "tifffile": "Fallback - Good for simple cases, limited pyramid support", 
            "openslide": "For reading pyramidal files only",
            "opencv-python": "Required for image transformations"
        }
    
    @staticmethod
    def install_instructions() -> str:
        """Get installation instructions for required libraries"""
        return """
To install the recommended libraries for pyramidal TIFF export:

1. Install pyvips (recommended):
   pip install pyvips
   
   Note: pyvips requires libvips to be installed on your system:
   - Windows: Download from https://github.com/libvips/libvips/releases
   - macOS: brew install vips
   - Ubuntu/Debian: apt-get install libvips-dev
   
2. Fallback option (tifffile):
   pip install tifffile
   
3. For transformations:
   pip install opencv-python

For best results, use pyvips as it provides true pyramidal TIFF support
with proper memory management and performance optimization.
"""