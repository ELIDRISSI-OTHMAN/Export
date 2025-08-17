"""
Group selection and transformation manager
"""

from typing import List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
import math

from .fragment import Fragment

class GroupManager(QObject):
    """Manages group selection and transformations"""
    
    group_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._selected_fragment_ids: List[str] = []
        
    def set_selected_fragments(self, fragment_ids: List[str]):
        """Set the selected fragment IDs"""
        self._selected_fragment_ids = fragment_ids.copy()
        self.group_changed.emit()
        
    def get_selected_fragment_ids(self) -> List[str]:
        """Get selected fragment IDs"""
        return self._selected_fragment_ids.copy()
        
    def has_group_selection(self) -> bool:
        """Check if multiple fragments are selected"""
        return len(self._selected_fragment_ids) > 1
        
    def get_group_size(self) -> int:
        """Get number of selected fragments"""
        return len(self._selected_fragment_ids)
        
    def clear_selection(self):
        """Clear all selections"""
        self._selected_fragment_ids.clear()
        self.group_changed.emit()
        
    def rotate_group(self, fragments: List[Fragment], angle_degrees: int):
        """Rotate the entire group around its center"""
        if not self.has_group_selection():
            return
            
        # Get selected fragments
        selected_fragments = [f for f in fragments if f.id in self._selected_fragment_ids]
        if len(selected_fragments) < 2:
            return
            
        print(f"Rotating group of {len(selected_fragments)} fragments by {angle_degrees}°")
        
        # Calculate group center
        group_center = self._calculate_group_center(selected_fragments)
        print(f"Group center: {group_center}")
        
        # Apply rotation to each fragment
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        for fragment in selected_fragments:
            # Get fragment center
            bbox = fragment.get_bounding_box()
            frag_center_x = bbox[0] + bbox[2] / 2
            frag_center_y = bbox[1] + bbox[3] / 2
            
            # Rotate fragment's individual rotation
            fragment.rotation = (fragment.rotation + angle_degrees) % 360
            fragment.invalidate_cache()
            
            # Calculate new position after group rotation
            rel_x = frag_center_x - group_center[0]
            rel_y = frag_center_y - group_center[1]
            
            new_rel_x = rel_x * cos_a - rel_y * sin_a
            new_rel_y = rel_x * sin_a + rel_y * cos_a
            
            new_center_x = group_center[0] + new_rel_x
            new_center_y = group_center[1] + new_rel_y
            
            # Update fragment position (adjust for new size after rotation)
            new_bbox = fragment.get_bounding_box()
            fragment.x = new_center_x - new_bbox[2] / 2
            fragment.y = new_center_y - new_bbox[3] / 2
            
            print(f"  {fragment.name}: moved to ({fragment.x:.1f}, {fragment.y:.1f})")
            
    def translate_group(self, fragments: List[Fragment], dx: float, dy: float):
        """Translate the entire group"""
        if not self.has_group_selection():
            return
            
        selected_fragments = [f for f in fragments if f.id in self._selected_fragment_ids]
        if len(selected_fragments) < 2:
            return
            
        print(f"Translating group of {len(selected_fragments)} fragments by ({dx}, {dy})")
        
        for fragment in selected_fragments:
            fragment.x += dx
            fragment.y += dy
            
    def _calculate_group_center(self, fragments: List[Fragment]) -> Tuple[float, float]:
        """Calculate the center point of the group"""
        total_x = 0.0
        total_y = 0.0
        
        for fragment in fragments:
            bbox = fragment.get_bounding_box()
            center_x = bbox[0] + bbox[2] / 2
            center_y = bbox[1] + bbox[3] / 2
            total_x += center_x
            total_y += center_y
            
        count = len(fragments)
        return (total_x / count, total_y / count)