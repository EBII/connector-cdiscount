from openerp import fields, models, api


class cdiscountBackend(models.Model):
    _name = 'cdiscount.backend'
    _description = 'cdiscount Backend'
    _inherit = 'connector.backend'

    _backend_type = 'cdiscount'

    @api.model
    def _select_versions(self):
        """ Available versions

        Can be inherited to add custom versions.
                         """
        return [('01/08/2016', 'Version Actuelle'),]

    version = fields.Selection(
         selection='_select_versions',
         string='Version',
         required=True,
    )
    location = fields.Char(string='Location')
    username = fields.Char(string='Username')
    password = fields.Char(string='Password')
    default_lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Default Language',
    )