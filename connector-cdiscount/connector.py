from openerp import models, fields
from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.checkpoint import checkpoint

class CdiscountBinding(models.AbstractModel):
    _name       = 'cdiscount.binding'
    _inherit    = 'external.binding'
    _description = 'Cdiscount Binding (abstract)'

    # 'openerp_id': openerp-side id must be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='cdiscount.backend',
        string='Cdiscount Backend',
        required=True,
        ondelete='restrict',
    )
    # fields.char because 0 is a valid cdiscount ID
    cdiscount_id = fields.Char(string='ID in the Cdiscount Machine',
                            select=True)


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with. """
    backend_record = session.env['cdiscount.backend'].browse(backend_id)
    env = ConnectorEnvironment(backend_record, session, model_name)
    lang = backend_record.default_lang_id
    lang_code = lang.code if lang else 'en_US'
    if lang_code == session.context.get('lang'):
        return env
    else:
        with env.session.change_context(lang=lang_code):
            return env

