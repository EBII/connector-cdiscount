
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter


class GenericAdapter(CRUDAdapter):

    _model_name = None
    _cdiscount_model = None
    _admin_path = None

    def search(self, filters=None):
        """ Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        return self._call('%s.search' % self._cdiscount_model,
                          [filters] if filters else [{}])

    def read(self, id, attributes=None):
        """ Returns the information of a record

        :rtype: dict
        """
        arguments = [int(id)]
        if attributes:
            # Avoid to pass Null values in attributes. Workaround for
            # https://bugs.launchpad.net/openerp-connector-magento/+bug/1210775
            # When Magento is installed on PHP 5.4 and the compatibility patch
            # http://magento.com/blog/magento-news/magento-now-supports-php-54
            # is not installed, calling info() with None in attributes
            # would return a wrong result (almost empty list of
            # attributes). The right correction is to install the
            # compatibility patch on Magento.
            arguments.append(attributes)
        return self._call('%s.info' % self._cdiscount_model,
                          arguments)

    def search_read(self, filters=None):
        """ Search records according to some criterias
        and returns their information"""
        return self._call('%s.list' % self._cdiscount_model, [filters])

    def create(self, data):
        """ Create a record on the external system """
        return self._call('%s.create' % self._cdiscount_model, [data])

    def write(self, id, data):
        """ Update records on the external system """
        return self._call('%s.update' % self._cdiscount_model,
                          [int(id), data])

    def delete(self, id):
        """ Delete a record on the external system """
        return self._call('%s.delete' % self._cdiscount_model, [int(id)])

    def admin_url(self, id):
        """ Return the URL in the Magento admin for a record """
        if self._admin_path is None:
            raise ValueError('No admin path is defined for this record')
        backend = self.backend_record
        url = backend.admin_location
        if not url:
            raise ValueError('No admin URL configured on the backend.')
        path = self._admin_path.format(model=self._cdiscount_model,
                                       id=id)
        url = url.rstrip('/')
        path = path.lstrip('/')
        url = '/'.join((url, path))
        return url
