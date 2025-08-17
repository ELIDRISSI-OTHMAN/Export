"""
Fragment management system
"""

from typing import Dict, List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
import numpy as np
import math

from .fragment import Fragment

class FragmentManager(QObject):
    """Manages all tissue fragments and their transformations"""
    
    fragments_changed = pyqtSignal()
    fragment_selected = pyqtSignal(str)  # fragment_id
    selection_changed = pyqtSignal()  # unified selection signal
    
    def __init__(self):
        super().__init__()
        self._fragments: Dict[str, Fragment] = {}
        self._selected_fragment_id: Optional[str] = None
        self._group_selection: List[str] = []  # Group selection
        
    def add_fragment_from_image(self, image_data: np.ndarray, name: str, 
                               file_path: str = "") -> str:
        """Add a new fragment from image data"""
        print(f"This is the file path: {file_path}")
        fragment = Fragment(
            name=name,
            image_data=image_data,
            file_path=file_path
        )
        
        self._fragments[fragment.id] = fragment
        
        # Auto-select first fragment
        if len(self._fragments) == 1:
            self.set_selected_fragment(fragment.id)
            
        self.fragments_changed.emit()
        return fragment.id
    
    # === SELECTION MANAGEMENT ===
    
    def select_single_fragment(self, fragment_id: str):
        """Select a single fragment, clearing any group selection"""
        # Clear all selections first
        self._clear_all_selections()
        
        # Set single selection
        if fragment_id in self._fragments:
            self._selected_fragment_id = fragment_id
            self._fragments[fragment_id].selected = True
            
        self.selection_changed.emit()
        self.fragments_changed.emit()
    
    def select_group(self, fragment_ids: List[str]):
        """Select multiple fragments as a group"""
        # Clear all selections first
        self._clear_all_selections()
        
        # Set group selection
        valid_ids = [fid for fid in fragment_ids if fid in self._fragments]
        if len(valid_ids) > 1:
            self._group_selection = valid_ids
            for fid in valid_ids:
                self._fragments[fid].selected = True
        elif len(valid_ids) == 1:
            # Single fragment - use single selection
            self.select_single_fragment(valid_ids[0])
            return
            
        self.selection_changed.emit()
        self.fragments_changed.emit()
    
    def clear_selection(self):
        """Clear all selections"""
        self._clear_all_selections()
        self.selection_changed.emit()
        self.fragments_changed.emit()
    
    def _clear_all_selections(self):
        """Internal method to clear all selection state"""
        # Clear visual selection on fragments
        for fragment in self._fragments.values():
            fragment.selected = False
            
        # Clear selection state
        self._selected_fragment_id = None
        self._group_selection = []
    
    def has_group_selection(self) -> bool:
        """Check if multiple fragments are selected"""
        return len(self._group_selection) > 1
    
    def has_single_selection(self) -> bool:
        """Check if exactly one fragment is selected"""
        return self._selected_fragment_id is not None
    
    def get_selected_fragment_ids(self) -> List[str]:
        """Get all selected fragment IDs"""
        if self.has_group_selection():
            return self._group_selection.copy()
        elif self.has_single_selection():
            return [self._selected_fragment_id]
        else:
            return []
    
    def get_selected_fragments(self) -> List[Fragment]:
        """Get all selected fragments"""
        ids = self.get_selected_fragment_ids()
        return [self._fragments[fid] for fid in ids if fid in self._fragments]
    
    # === TRANSFORMATION METHODS ===
    
    def apply_group_rotation(self, angle_degrees: int):
        """Apply rotation to the entire group around group center"""
        if not self.has_group_selection():
            return
            
        fragments = self.get_selected_fragments()
        if len(fragments) < 2:
            return
            
        print(f"Applying {angle_degrees}° rotation to group of {len(fragments)} fragments")
        
        # Calculate group center (center of all fragment centers)
        total_x, total_y = 0.0, 0.0
        for fragment in fragments:
            bbox = fragment.get_bounding_box()
            center_x = bbox[0] + bbox[2] / 2
            center_y = bbox[1] + bbox[3] / 2
            total_x += center_x
            total_y += center_y
            
        group_center_x = total_x / len(fragments)
        group_center_y = total_y / len(fragments)
        
        print(f"Group center: ({group_center_x:.1f}, {group_center_y:.1f})")
        
        # Apply rotation to each fragment
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        for fragment in fragments:
            # Get current fragment center
            bbox = fragment.get_bounding_box()
            frag_center_x = bbox[0] + bbox[2] / 2
            frag_center_y = bbox[1] + bbox[3] / 2
            
            # Rotate fragment's individual rotation
            fragment.rotation = (fragment.rotation + angle_degrees) % 360
            fragment.invalidate_cache()
            
            # Calculate new position after group rotation
            # Translate to origin (relative to group center)
            rel_x = frag_center_x - group_center_x
            rel_y = frag_center_y - group_center_y
            
            # Rotate around origin
            new_rel_x = rel_x * cos_a - rel_y * sin_a
            new_rel_y = rel_x * sin_a + rel_y * cos_a
            
            # Calculate new fragment center position
            new_center_x = group_center_x + new_rel_x
            new_center_y = group_center_y + new_rel_y
            
            # Get new bounding box after individual rotation
            new_bbox = fragment.get_bounding_box()
            
            # Set new position (top-left corner)
            fragment.x = new_center_x - new_bbox[2] / 2
            fragment.y = new_center_y - new_bbox[3] / 2
            
            print(f"  {fragment.name}: moved to ({fragment.x:.1f}, {fragment.y:.1f})")
        
        self.fragments_changed.emit()
    
    def apply_group_translation(self, dx: float, dy: float):
        """Apply translation to the entire group"""
        if not self.has_group_selection():
            return
            
        fragments = self.get_selected_fragments()
        if len(fragments) < 2:
            return
            
        print(f"Applying translation ({dx}, {dy}) to group of {len(fragments)} fragments")
        
        for fragment in fragments:
            fragment.x += dx
            fragment.y += dy
            
        self.fragments_changed.emit()
    
    def apply_single_rotation(self, angle_degrees: int):
        """Apply rotation to single selected fragment"""
        if not self.has_single_selection():
            return
            
        fragment = self._fragments.get(self._selected_fragment_id)
        if fragment:
            fragment.rotation = (fragment.rotation + angle_degrees) % 360
            fragment.invalidate_cache()
            self.fragments_changed.emit()
    
    def apply_single_translation(self, dx: float, dy: float):
        """Apply translation to single selected fragment"""
        if not self.has_single_selection():
            return
            
        fragment = self._fragments.get(self._selected_fragment_id)
        if fragment:
            fragment.x += dx
            fragment.y += dy
            self.fragments_changed.emit()
    
    # === LEGACY COMPATIBILITY METHODS ===
    def get_fragment(self, fragment_id: str) -> Optional[Fragment]:
        """Get fragment by ID"""
        return self._fragments.get(fragment_id)
    
    def get_all_fragments(self) -> List[Fragment]:
        """Get all fragments"""
        return list(self._fragments.values())
    
    def get_visible_fragments(self) -> List[Fragment]:
        """Get only visible fragments"""
        return [f for f in self._fragments.values() if f.visible]
    
    def remove_fragment(self, fragment_id: str) -> bool:
        """Remove a fragment"""
        if fragment_id in self._fragments:
            del self._fragments[fragment_id]
            
            # Update selection if removed fragment was selected
            if self._selected_fragment_id == fragment_id:
                remaining_ids = list(self._fragments.keys())
                self._selected_fragment_id = remaining_ids[0] if remaining_ids else None
                
            self.fragments_changed.emit()
            return True
        return False
    
    def set_selected_fragment(self, fragment_id: Optional[str]):
        """Legacy method - use select_single_fragment instead"""
        if fragment_id:
            self.select_single_fragment(fragment_id)
        else:
            self.clear_selection()
    
    def get_selected_fragment_id(self) -> Optional[str]:
        """Get the selected fragment ID"""
        return self._selected_fragment_id
    
    def get_selected_fragment(self) -> Optional[Fragment]:
        """Get the selected fragment"""
        if self._selected_fragment_id:
            return self._fragments.get(self._selected_fragment_id)
        return None
    
    def set_fragment_visibility(self, fragment_id: str, visible: bool):
        """Set fragment visibility"""
        fragment = self._fragments.get(fragment_id)
        if fragment:
            fragment.visible = visible
            self.fragments_changed.emit()
    
    def set_fragment_position(self, fragment_id: str, x: float, y: float):
        """Set fragment position"""
        fragment = self._fragments.get(fragment_id)
        if fragment:
            # Store positions as floats without excessive rounding
            fragment.x = float(x)
            fragment.y = float(y)
            
            self.fragments_changed.emit()
    
    def translate_fragment(self, fragment_id: str, dx: float, dy: float):
        """Translate fragment by offset"""
        fragment = self._fragments.get(fragment_id)
        if fragment:
            fragment.x = fragment.x + float(dx)
            fragment.y = fragment.y + float(dy)
            
            self.fragments_changed.emit()
    
    def rotate_fragment(self, fragment_id: str, angle: int):
        """Rotate fragment by angle (90 degree increments)"""
        fragment = self._fragments.get(fragment_id)
        if fragment:
            fragment.rotation = (fragment.rotation + angle) % 360.0
            fragment.invalidate_cache()
            self.fragments_changed.emit()
    
    def set_fragment_rotation(self, fragment_id: str, angle: float):
        """Set fragment rotation to specific angle"""
        fragment = self._fragments.get(fragment_id)
        if fragment:
            fragment.rotation = angle % 360.0
            fragment.invalidate_cache()
            self.fragments_changed.emit()
    
    def flip_fragment(self, fragment_id: str, horizontal: bool = True):
        """Flip fragment horizontally or vertically"""
        fragment = self._fragments.get(fragment_id)
        if fragment:
            if horizontal:
                fragment.flip_horizontal = not fragment.flip_horizontal
            else:
                fragment.flip_vertical = not fragment.flip_vertical
            fragment.invalidate_cache()
            self.fragments_changed.emit()
    
    def set_fragment_transform(self, fragment_id: str, rotation: int = None,
                              translation: Tuple[float, float] = None,
                              flip_horizontal: bool = None,
                              flip_vertical: bool = None):
        """Set complete fragment transformation"""
        fragment = self._fragments.get(fragment_id)
        if fragment:
            transform_changed = False
            if rotation is not None:
                fragment.rotation = float(rotation) % 360.0
                transform_changed = True
            if translation is not None:
                fragment.x = float(translation[0])
                fragment.y = float(translation[1])
            if flip_horizontal is not None:
                fragment.flip_horizontal = flip_horizontal
                transform_changed = True
            if flip_vertical is not None:
                fragment.flip_vertical = flip_vertical
                transform_changed = True
            # Only invalidate cache when transforms that affect the image are changed
            if transform_changed:
                fragment.invalidate_cache()
            self.fragments_changed.emit()
    
    def reset_fragment_transform(self, fragment_id: str):
        """Reset fragment transformation to default"""
        fragment = self._fragments.get(fragment_id)
        if fragment:
            fragment.reset_transform()
            self.fragments_changed.emit()
    
    def reset_all_transforms(self):
        """Reset all fragment transformations"""
        for fragment in self._fragments.values():
            fragment.reset_transform()
        self.fragments_changed.emit()
    
    def get_composite_bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box of all visible fragments (min_x, min_y, max_x, max_y)"""
        if not self._fragments:
            return (0, 0, 0, 0)
            
        visible_fragments = self.get_visible_fragments()
        if not visible_fragments:
            return (0, 0, 0, 0)
            
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for fragment in visible_fragments:
            bbox_x, bbox_y, bbox_w, bbox_h = fragment.get_bounding_box()
            min_x = min(min_x, bbox_x)
            min_y = min(min_y, bbox_y)
            max_x = max(max_x, bbox_x + bbox_w)
            max_y = max(max_y, bbox_y + bbox_h)
            
        return (min_x, min_y, max_x, max_y)
    
    def export_metadata(self) -> dict:
        """Export fragment metadata for serialization"""
        return {
            'fragments': [fragment.to_dict() for fragment in self._fragments.values()],
            'selected_fragment_id': self._selected_fragment_id,
            'version': '1.0'
        }
    
    def import_metadata(self, metadata: dict):
        """Import fragment metadata"""
        self._fragments.clear()
        
        for fragment_data in metadata.get('fragments', []):
            fragment = Fragment.from_dict(fragment_data)
            self._fragments[fragment.id] = fragment
            
        selected_id = metadata.get('selected_fragment_id')
        if selected_id and selected_id in self._fragments:
            self.set_selected_fragment(selected_id)
            
        self.fragments_changed.emit()