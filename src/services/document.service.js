import api from './api.service';

class DocumentService {
  /**
   * Get all documents for a user
   * @param {number} userId 
   * @returns {Promise}
   */
  getUserDocuments(userId) {
    return api.get(`/admin/users/${userId}/documents`);
  }

  /**
   * View a specific document
   * @param {number} documentId 
   * @returns {Promise}
   */
  viewDocument(documentId) {
    // This will return the document file for viewing
    return api.get(`/documents/${documentId}`);
  }

  /**
   * Toggle document verification status
   * @param {number} documentId 
   * @param {boolean} verified 
   * @returns {Promise}
   */
  verifyDocument(documentId, verified) {
    return api.put(`/admin/documents/${documentId}/verify`, { verified });
  }

  /**
   * Get professional documents with verification status
   * @param {number} professionalId 
   * @returns {Promise}
   */
  getProfessionalVerificationStatus(professionalId) {
    return api.get(`/admin/professionals/${professionalId}/verification`);
  }

  /**
   * Upload a new document
   * @param {number} userId 
   * @param {File} file 
   * @param {string} documentType 
   * @returns {Promise}
   */
  uploadDocument(userId, file, documentType) {
    const formData = new FormData();
    formData.append('document', file);
    formData.append('documentType', documentType);
    
    return api.post(`/users/${userId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
}

export default new DocumentService();
